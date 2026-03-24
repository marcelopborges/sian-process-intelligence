"""
Orquestração do pipeline semântico SX3: discovery → model → process → persistência.

Entradas/saídas padronizadas via argumentos CLI (ver `parse_args`).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

from app.config.domain_config import resolve_tables_for_run
from app.discovery.infer_events import (
    apply_min_score,
    apply_top_n_per_table,
    infer_event_candidates,
)
from app.discovery.sx3_loader import build_sx3_metadata, load_sx3_csv
from app.lab import config as local_lab_config
from app.model.enrich_events import build_enriched_records
from app.model.event_aggregation import build_event_log_records, event_log_to_jsonable
from app.paths import repo_root
from app.presentation.export_diagram import (
    load_event_log_json,
    write_process_flow_artifacts,
)
from app.process.build_flow import ProcessFlowPayload, build_process_flow, payload_to_json_dict
from app.validation.validate_sequences import validate_linear_edges

logger = logging.getLogger(__name__)
REPO_ROOT = repo_root()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Pipeline SX3: inferência → event log → fluxo (app.pipeline.runner)."
    )
    p.add_argument("--input", type=Path, default=None, help="Alias de --sx3 (CSV SX3).")
    p.add_argument("--output", "-o", type=Path, default=None, help="Diretório de saída padronizado.")
    p.add_argument(
        "--sx3",
        "--sx3-csv",
        type=Path,
        dest="sx3_csv",
        default=None,
        help="CSV SX3.",
    )
    p.add_argument("--duckdb-path", type=Path, default=None)
    p.add_argument("--domains-yaml", type=Path, default=None)
    p.add_argument("--domain", type=str, default=None)
    p.add_argument("--include-tables", type=str, default=None)
    p.add_argument("--min-score", type=float, default=0.0)
    p.add_argument("--top-n-per-table", type=int, default=None)
    p.add_argument("--use-llm", action="store_true")
    p.add_argument("--build-event-log", action="store_true")
    p.add_argument("--top-attributes-per-event", type=int, default=8)
    p.add_argument("--build-process-flow", action="store_true")
    p.add_argument(
        "--validate",
        action="store_true",
        help="Após o fluxo: grava validation_report.json (arestas + resumo dbt).",
    )
    return p.parse_args(argv)


def _parse_include_tables(s: str | None) -> list[str] | None:
    if not s:
        return None
    parts = [p.strip() for p in s.split(",")]
    return [p for p in parts if p]


def run_pipeline(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)

    out_dir = args.output or Path("data/outputs/sx3_semantic")
    sx3_path = args.input or args.sx3_csv or Path("data/others/SX3010_202603231122.csv")

    use_llm = bool(args.use_llm) and not args.build_event_log
    if args.use_llm and args.build_event_log:
        logger.info("--build-event-log ativo: LLM desligado.")

    try:
        import duckdb
    except ImportError as e:
        raise SystemExit("duckdb não instalado.") from e

    duckdb_path = args.duckdb_path or local_lab_config.DUCKDB_PATH

    if not sx3_path.exists():
        raise FileNotFoundError(f"SX3 CSV não encontrado: {sx3_path}")
    if not duckdb_path.exists():
        raise FileNotFoundError(f"DuckDB não encontrado: {duckdb_path}")

    domains_yaml = args.domains_yaml or (REPO_ROOT / "config" / "domains.yaml")
    include_list = _parse_include_tables(args.include_tables)
    allowed = resolve_tables_for_run(
        domain=args.domain,
        include_tables=include_list,
        domains_path=domains_yaml,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    sx3_df = load_sx3_csv(sx3_path)
    sx3_meta = build_sx3_metadata(sx3_df)

    conn = duckdb.connect(str(duckdb_path), read_only=True)
    duckdb_cols: dict[str, set[str]] = {}
    for (t,) in conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name LIKE 'stg_%' ORDER BY table_name"
    ).fetchall():
        base = t[4:].upper()
        cols = {str(row[0]).upper() for row in conn.execute(f"DESCRIBE {t}").fetchall()}
        duckdb_cols[base] = cols
    conn.close()

    raw = infer_event_candidates(
        sx3_meta=sx3_meta,
        duckdb_columns_by_table=duckdb_cols,
        allowed_tables=allowed,
    )
    raw = apply_min_score(raw, args.min_score)
    top_n = None if args.build_event_log else args.top_n_per_table
    raw = apply_top_n_per_table(raw, top_n)

    enriched = build_enriched_records(
        raw,
        duckdb_cols,
        mart_domain=args.domain or "cp",
        domains_yaml=domains_yaml,
        use_llm=use_llm,
    )

    conn = duckdb.connect(str(duckdb_path), read_only=False)
    conn.execute(
        """
        CREATE OR REPLACE TABLE sx3_event_candidates (
          candidate_id VARCHAR, activity VARCHAR, event_type_suggested VARCHAR,
          source_table VARCHAR, source_column VARCHAR, column_role VARCHAR,
          heuristic_score DOUBLE, reason VARCHAR, dbt_classification VARCHAR,
          justification VARCHAR, confidence_level VARCHAR, semantic_description VARCHAR,
          llm_revised_confidence DOUBLE, llm_audit_json VARCHAR, created_at_utc VARCHAR
        )
        """
    )
    rows = [
        (
            e.candidate_id,
            e.activity,
            e.event_type_suggested,
            e.source_table,
            e.source_column,
            e.column_role,
            float(e.heuristic_score),
            e.reason,
            e.dbt_classification,
            e.justification,
            e.confidence_level,
            e.semantic_description,
            e.llm_revised_confidence,
            json.dumps(e.llm_audit, ensure_ascii=False) if e.llm_audit else None,
            e.created_at_utc,
        )
        for e in enriched
    ]
    if rows:
        conn.executemany(
            """
            INSERT INTO sx3_event_candidates
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    event_records = None
    if args.build_event_log:
        top_attr = args.top_attributes_per_event if args.top_attributes_per_event > 0 else None
        event_records = build_event_log_records(enriched, top_attributes_per_event=top_attr)
        conn.execute(
            """
            CREATE OR REPLACE TABLE event_log_candidates (
              activity VARCHAR, event_status VARCHAR, event_time_table VARCHAR,
              event_time_column VARCHAR, attributes_json VARCHAR, source_tables_json VARCHAR,
              confidence VARCHAR, dbt_alignment VARCHAR
            )
            """
        )
        erows = []
        for r in event_records:
            et = r.event_time
            erows.append(
                (
                    r.activity,
                    r.event_status,
                    et["table"] if et else None,
                    et["column"] if et else None,
                    json.dumps(r.attributes, ensure_ascii=False),
                    json.dumps(r.source_tables, ensure_ascii=False),
                    r.confidence,
                    r.dbt_alignment,
                )
            )
        if erows:
            conn.executemany(
                "INSERT INTO event_log_candidates VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                erows,
            )
        el_path = out_dir / "event_log_candidates.json"
        with el_path.open("w", encoding="utf-8") as f:
            json.dump(event_log_to_jsonable(event_records), f, ensure_ascii=False, indent=2)

    flow_payload: ProcessFlowPayload | None = None
    if args.build_process_flow:
        if args.build_event_log and event_records is not None:
            events_pf = event_log_to_jsonable(event_records)
        else:
            elp = out_dir / "event_log_candidates.json"
            if not elp.exists():
                raise SystemExit(f"--build-process-flow requer event log em {elp} ou --build-event-log")
            events_pf = load_event_log_json(elp)
        sx3_rows = [asdict(e) for e in enriched]
        flow_payload = build_process_flow(
            events_pf,
            duckdb_columns_by_table=duckdb_cols,
            sx3_candidate_rows=sx3_rows,
        )
        write_process_flow_artifacts(flow_payload, out_dir)
        conn.execute(
            """
            CREATE OR REPLACE TABLE process_flow_snapshot (
              generated_at_utc VARCHAR, payload_json VARCHAR
            )
            """
        )
        conn.execute(
            "INSERT INTO process_flow_snapshot VALUES (?, ?)",
            [
                flow_payload.generated_at_utc,
                json.dumps(payload_to_json_dict(flow_payload), ensure_ascii=False),
            ],
        )

    conn.close()

    json_path = out_dir / "sx3_event_candidates.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in enriched], f, ensure_ascii=False, indent=2)

    if args.validate:
        val_dir = out_dir / "validation"
        val_dir.mkdir(parents=True, exist_ok=True)
        dbt_summary: dict[str, int] = {}
        for e in enriched:
            k = str(e.dbt_classification or "")
            dbt_summary[k] = dbt_summary.get(k, 0) + 1
        edge_issues: list[str] = []
        if flow_payload is not None:
            edge_issues = validate_linear_edges(flow_payload.edges)
        report = {
            "candidates_total": len(enriched),
            "dbt_classification_counts": dbt_summary,
            "process_flow_edges": len(flow_payload.edges) if flow_payload else 0,
            "linear_edge_issues": edge_issues,
        }
        vpath = val_dir / "validation_report.json"
        with vpath.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        if edge_issues:
            logger.warning("Validação: %s problema(s) na cadeia linear.", len(edge_issues))

    print(f"OK: candidatos={len(enriched)} → {out_dir}")
    return 0


def main() -> None:
    sys.exit(run_pipeline())


if __name__ == "__main__":
    main()
