#!/usr/bin/env python3
"""
Inferência de candidatos a eventos de processo a partir do dicionário SX3 (Protheus).

Pipeline: SX3 CSV → heurística por keywords → filtros (domínio CP, score, top-N) →
alinhamento mart (staging) → `column_role` (EVENT_TIME / ATTRIBUTE / …) →
saída JSON/MD/DuckDB (`sx3_event_candidates`).

Com `--build-event-log`: agrega 1 registro por `activity` com `event_time` + `attributes`
→ `event_log_candidates.json` e tabela `event_log_candidates` (sem LLM).

Com `--build-process-flow` (com `--build-event-log` ou `event_log_candidates.json` já existente):
→ `process_flow.json`, `process_flow.md` (Mermaid), tabela `process_flow_snapshot`.

Opcional: `--use-llm` para texto semântico (desativado se `--build-event-log`).
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.sx3.sx3_loader import build_sx3_metadata, load_sx3_csv
from python.validation.column_role import classify_column_role
from python.validation.dbt_alignment import classify_event_candidate, load_mart_registry
from python.validation.domain_config import resolve_tables_for_run
from python.validation.event_log_builder import (
    build_event_log_records,
    event_log_to_jsonable,
)
from python.validation.llm_enrichment import audit_dict, enrich_candidate
from python.validation.process_flow import (
    build_process_flow,
    load_event_log_json,
    payload_to_json_dict,
    write_process_flow_artifacts,
)

from python.local_lab import config as local_lab_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventCandidateRaw:
    candidate_id: str
    activity: str
    source_table: str
    source_column: str
    confidence: float
    reason: str
    created_at_utc: str


@dataclass
class EventCandidateEnriched:
    candidate_id: str
    activity: str
    event_type_suggested: str
    source_table: str
    source_column: str
    column_role: str
    heuristic_score: float
    reason: str
    dbt_classification: str
    justification: str
    confidence_level: str
    semantic_description: str
    llm_revised_confidence: float | None
    llm_audit: dict[str, Any] | None
    created_at_utc: str


def _norm(s: Any) -> str:
    return "" if s is None else str(s).strip()


def _contains_any_keywords(haystack: str, keywords: list[str]) -> bool:
    up = haystack.upper()
    return any(k in up for k in keywords)


def infer_event_candidates(
    *,
    sx3_meta: dict[str, dict[str, Any]],
    duckdb_columns_by_table: dict[str, set[str]],
    allowed_tables: set[str] | None = None,
) -> list[EventCandidateRaw]:
    """
    Heurística por keywords em X3_TITULO/X3_DESCRIC.
    Se `allowed_tables` for definido, apenas essas tabelas (códigos Protheus) são consideradas.
    """
    now = datetime.now(timezone.utc).isoformat()

    expected_table: dict[str, str] = {
        "TITULO_CRIADO": "SE2",
        "TITULO_LIBERADO": "SE2",
        "LANCAMENTO_CONTABIL": "FK2",
        "PAGAMENTO_REALIZADO": "SE5",
        "BAIXA_SEM_SE5": "SE2",
    }

    keyword_map: dict[str, list[str]] = {
        "TITULO_CRIADO": ["EMISSAO", "EMISSA", "EMIT"],
        "TITULO_LIBERADO": ["LIBERACAO", "LIBERAC", "DATALIB", "DT LIBERAC"],
        "LANCAMENTO_CONTABIL": ["LANC", "DIARIO", "CONTABIL"],
        "PAGAMENTO_REALIZADO": [
            "PAGAMENTO",
            "MOVIMENTACAO",
            "CREDITO",
            "DEBITO",
            "BANCO",
            "DATA DA MOVIMENT",
        ],
        "BAIXA_SEM_SE5": ["BAIXA", "DATA DE BAIXA", "STATUS DA BAIXA"],
        "EVENTO_FINANCEIRO_GERADO": ["EVENTO", "FINANCEIRO", "GERADO"],
    }

    out: list[EventCandidateRaw] = []

    def add(activity: str, table: str, column: str, confidence: float, reason: str) -> None:
        if allowed_tables is not None and table.upper() not in allowed_tables:
            return
        out.append(
            EventCandidateRaw(
                candidate_id=f"{activity}:{table}.{column}:{len(out)}",
                activity=activity,
                source_table=table,
                source_column=column,
                confidence=float(confidence),
                reason=reason,
                created_at_utc=now,
            )
        )

    for table, fields in sx3_meta.items():
        if allowed_tables is not None and table.upper() not in allowed_tables:
            continue
        for col, meta in fields.items():
            titulo = getattr(meta, "titulo", None) or ""
            desc = getattr(meta, "desc", None) or ""
            desc_eng = getattr(meta, "desc_eng", None) or ""
            combined = f"{titulo} {desc} {desc_eng}".strip()
            if not combined:
                continue
            for activity, kws in keyword_map.items():
                if activity == "EVENTO_FINANCEIRO_GERADO":
                    continue
                if _contains_any_keywords(combined, kws):
                    boost = (
                        0.15 if re.search(r"\bDT\b|DATA", (titulo + " " + desc).upper()) else 0.0
                    )
                    expected_boost = 0.20 if expected_table.get(activity) == table else 0.0
                    confidence = min(1.0, 0.45 + boost + expected_boost)
                    add(
                        activity,
                        table,
                        col,
                        confidence=confidence,
                        reason="keyword_match:"
                        + kws[0]
                        + (
                            f";expected_table_boost:{expected_boost:.2f}" if expected_boost else ""
                        ),
                    )
                    break

    fk7_cols = duckdb_columns_by_table.get("FK7", set())
    tech_col = "F7_DBALTERACAO" if "F7_DBALTERACAO" in fk7_cols else None
    if tech_col is None and "DBALTERACAO" in fk7_cols:
        tech_col = "DBALTERACAO"
    if tech_col:
        add(
            "EVENTO_FINANCEIRO_GERADO",
            "FK7",
            tech_col,
            confidence=0.30,
            reason=(
                f"tech_ts_match:FK7.{tech_col} (atividade também depende de F7_COD_EVENTO no mart)"
            ),
        )

    return out


def apply_min_score(candidates: list[EventCandidateRaw], min_score: float) -> list[EventCandidateRaw]:
    return [c for c in candidates if c.confidence >= min_score]


def apply_top_n_per_table(
    candidates: list[EventCandidateRaw],
    top_n: int | None,
) -> list[EventCandidateRaw]:
    if top_n is None or top_n <= 0:
        return candidates
    by_table: dict[str, list[EventCandidateRaw]] = defaultdict(list)
    for c in candidates:
        by_table[c.source_table.upper()].append(c)
    out: list[EventCandidateRaw] = []
    for tbl in sorted(by_table.keys()):
        rows = sorted(by_table[tbl], key=lambda x: -x.confidence)[:top_n]
        out.extend(rows)
    return out


def build_enriched_records(
    raw_list: list[EventCandidateRaw],
    duckdb_columns_by_table: dict[str, set[str]],
    mart_domain: str | None,
    domains_yaml: Path | None,
    use_llm: bool,
) -> list[EventCandidateEnriched]:
    mart = load_mart_registry(domain=mart_domain or "cp", domains_yaml_path=domains_yaml)
    enriched: list[EventCandidateEnriched] = []
    for raw in raw_list:
        cls, just, conf_level = classify_event_candidate(
            activity=raw.activity,
            source_table=raw.source_table,
            source_column=raw.source_column,
            duckdb_columns_by_table=duckdb_columns_by_table,
            mart=mart,
        )
        role = classify_column_role(raw.source_column)
        llm = enrich_candidate(
            activity=raw.activity,
            source_table=raw.source_table,
            source_column=raw.source_column,
            heuristic_score=raw.confidence,
            dbt_classification=cls,
            justification=just,
            confidence_level=conf_level,
            use_llm=use_llm,
        )
        audit = audit_dict(llm.audit) if use_llm else None
        enriched.append(
            EventCandidateEnriched(
                candidate_id=raw.candidate_id,
                activity=raw.activity,
                event_type_suggested=raw.activity,
                source_table=raw.source_table,
                source_column=raw.source_column,
                column_role=role,
                heuristic_score=raw.confidence,
                reason=raw.reason,
                dbt_classification=cls,
                justification=just,
                confidence_level=conf_level,
                semantic_description=llm.semantic_description,
                llm_revised_confidence=llm.revised_confidence,
                llm_audit=audit,
                created_at_utc=raw.created_at_utc,
            )
        )
    return enriched


def _parse_include_tables(s: str | None) -> list[str] | None:
    if not s:
        return None
    parts = [p.strip() for p in s.split(",")]
    return [p for p in parts if p]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inferir candidatos a eventos a partir do SX3 (heurística + alinhamento dbt)."
    )
    parser.add_argument(
        "--sx3",
        "--sx3-csv",
        type=Path,
        dest="sx3_csv",
        default=Path("data/others/SX3010_202603231122.csv"),
        help="Caminho do arquivo CSV exportado do SX3.",
    )
    parser.add_argument(
        "--duckdb-path",
        type=Path,
        default=None,
        help="Caminho do DuckDB local (default: local/process_intelligence.duckdb).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("output") / "sx3_semantic",
        help="Diretório de saída JSON/Markdown.",
    )
    parser.add_argument(
        "--domains-yaml",
        type=Path,
        default=None,
        help="Override do caminho para config/domains.yaml.",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Domínio declarado em domains.yaml (ex.: cp). Filtra tabelas conhecidas.",
    )
    parser.add_argument(
        "--include-tables",
        type=str,
        default=None,
        help="Lista explícita de tabelas Protheus (ex.: SE2,FK7,FK2,SE5). Sobrescreve --domain.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Score heurístico mínimo (0-1).",
    )
    parser.add_argument(
        "--top-n-per-table",
        type=int,
        default=None,
        help="Máximo de candidatos por tabela após ordenar por score (omitir = sem limite).",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enriquecer com LLM (OPENAI_API_KEY). Sem chave, gera texto por regras.",
    )
    parser.add_argument(
        "--build-event-log",
        action="store_true",
        help="Agrega 1 registro por activity em event_log_candidates.json + tabela DuckDB (sem LLM).",
    )
    parser.add_argument(
        "--top-attributes-per-event",
        type=int,
        default=8,
        help="Máximo de colunas ATTRIBUTE por evento (com --build-event-log). Default: 8.",
    )
    parser.add_argument(
        "--build-process-flow",
        action="store_true",
        help="Gera process_flow.json, process_flow.md (Mermaid) e tabela process_flow_snapshot (requer event log).",
    )
    args = parser.parse_args()

    use_llm = bool(args.use_llm) and not args.build_event_log
    if args.use_llm and args.build_event_log:
        logger.info("--build-event-log ativo: LLM desligado (pipeline de event log sem LLM).")

    try:
        import duckdb
    except ImportError as e:
        raise SystemExit("duckdb não instalado. Instale com: pip install duckdb") from e

    duckdb_path = args.duckdb_path or local_lab_config.DUCKDB_PATH

    if not args.sx3_csv.exists():
        raise FileNotFoundError(f"SX3 CSV não encontrado: {args.sx3_csv}")
    if not duckdb_path.exists():
        raise FileNotFoundError(
            f"DuckDB não encontrado: {duckdb_path}. Gere o laboratório local ou ajuste --duckdb-path."
        )

    domains_yaml = args.domains_yaml or (REPO_ROOT / "config" / "domains.yaml")
    include_list = _parse_include_tables(args.include_tables)
    allowed = resolve_tables_for_run(
        domain=args.domain,
        include_tables=include_list,
        domains_path=domains_yaml,
    )
    if args.domain and not include_list:
        logger.info("Filtro de domínio '%s': tabelas %s", args.domain, sorted(allowed or []))
    if include_list:
        logger.info("Filtro explícito de tabelas: %s", sorted(allowed or []))

    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sx3_df = load_sx3_csv(args.sx3_csv)
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
    logger.info("Candidatos brutos (após filtro de tabelas): %s", len(raw))

    raw = apply_min_score(raw, args.min_score)
    top_n = None if args.build_event_log else args.top_n_per_table
    if args.build_event_log and args.top_n_per_table:
        logger.info(
            "Com --build-event-log, ignorando --top-n-per-table para preservar candidatos a EVENT_TIME."
        )
    raw = apply_top_n_per_table(raw, top_n)
    logger.info("Candidatos após min-score e top-n: %s", len(raw))

    enriched = build_enriched_records(
        raw,
        duckdb_cols,
        mart_domain=args.domain or "cp",
        domains_yaml=domains_yaml,
        use_llm=use_llm,
    )

    # Persistência DuckDB
    conn = duckdb.connect(str(duckdb_path), read_only=False)
    conn.execute(
        """
        CREATE OR REPLACE TABLE sx3_event_candidates (
          candidate_id VARCHAR,
          activity VARCHAR,
          event_type_suggested VARCHAR,
          source_table VARCHAR,
          source_column VARCHAR,
          column_role VARCHAR,
          heuristic_score DOUBLE,
          reason VARCHAR,
          dbt_classification VARCHAR,
          justification VARCHAR,
          confidence_level VARCHAR,
          semantic_description VARCHAR,
          llm_revised_confidence DOUBLE,
          llm_audit_json VARCHAR,
          created_at_utc VARCHAR
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

    if args.build_event_log:
        top_attr = args.top_attributes_per_event if args.top_attributes_per_event > 0 else None
        event_records = build_event_log_records(enriched, top_attributes_per_event=top_attr)
        conn.execute(
            """
            CREATE OR REPLACE TABLE event_log_candidates (
              activity VARCHAR,
              event_status VARCHAR,
              event_time_table VARCHAR,
              event_time_column VARCHAR,
              attributes_json VARCHAR,
              source_tables_json VARCHAR,
              confidence VARCHAR,
              dbt_alignment VARCHAR
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
                """
                INSERT INTO event_log_candidates
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                erows,
            )
        el_path = out_dir / "event_log_candidates.json"
        with el_path.open("w", encoding="utf-8") as f:
            json.dump(event_log_to_jsonable(event_records), f, ensure_ascii=False, indent=2)
        logger.info(
            "Event log candidato: %s registros → %s e tabela event_log_candidates",
            len(event_records),
            el_path,
        )

    if args.build_process_flow:
        if args.build_event_log:
            events_pf = event_log_to_jsonable(event_records)
        else:
            elp = out_dir / "event_log_candidates.json"
            if not elp.exists():
                raise SystemExit(
                    "--build-process-flow exige --build-event-log nesta execução ou "
                    f"arquivo existente: {elp}"
                )
            events_pf = load_event_log_json(elp)
        sx3_rows = [asdict(e) for e in enriched]
        payload = build_process_flow(
            events_pf,
            duckdb_columns_by_table=duckdb_cols,
            sx3_candidate_rows=sx3_rows,
        )
        pj, pm = write_process_flow_artifacts(payload, out_dir)
        conn.execute(
            """
            CREATE OR REPLACE TABLE process_flow_snapshot (
              generated_at_utc VARCHAR,
              payload_json VARCHAR
            )
            """
        )
        conn.execute(
            "INSERT INTO process_flow_snapshot VALUES (?, ?)",
            [payload.generated_at_utc, json.dumps(payload_to_json_dict(payload), ensure_ascii=False)],
        )
        logger.info("Fluxo de processo: %s, %s e tabela process_flow_snapshot", pj, pm)

    conn.close()

    json_path = out_dir / "sx3_event_candidates.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in enriched], f, ensure_ascii=False, indent=2)

    md_path = out_dir / "sx3_event_candidates.md"
    top = sorted(enriched, key=lambda x: -x.heuristic_score)[:80]
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Sugestões de eventos (SX3) — enriquecido com alinhamento dbt\n\n")
        f.write(f"- total_candidatos: {len(enriched)}\n")
        f.write(f"- domain: {args.domain or '(não filtrado)'}\n")
        f.write(f"- min_score: {args.min_score}\n\n")
        f.write(
            "| activity | score | dbt | conf | table | column | justificativa (resumo) |\n"
        )
        f.write("|---|---:|---|---:|---|---|---|\n")
        for e in top:
            j = (e.justification[:80] + "…") if len(e.justification) > 80 else e.justification
            f.write(
                f"| {e.activity} | {e.heuristic_score:.2f} | {e.dbt_classification} | "
                f"{e.confidence_level} | {e.source_table} | {e.source_column} | {j} |\n"
            )

    print(f"Inferência concluída. candidatos: {len(enriched)}")
    print(f"DuckDB: {duckdb_path} (tabela sx3_event_candidates)")
    print(f"Arquivos: {json_path} e {md_path}")
    if args.build_event_log:
        print(f"Event log: {out_dir / 'event_log_candidates.json'} (tabela event_log_candidates)")
    if args.build_process_flow:
        print(f"Fluxo: {out_dir / 'process_flow.json'} / {out_dir / 'process_flow.md'}")


if __name__ == "__main__":
    main()
