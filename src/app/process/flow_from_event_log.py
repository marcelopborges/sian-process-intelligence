"""
Gera artefatos de fluxo (JSON/MD + snapshot DuckDB) a partir de `event_log_candidates.json`.

Lógica executada pelos scripts; não deve ficar em `scripts/`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.lab import config as local_lab_config
from app.presentation.export_diagram import (
    load_event_log_json,
    load_sx3_candidates_json,
    write_process_flow_artifacts,
)
from app.process.build_flow import build_process_flow, payload_to_json_dict


def duckdb_staging_columns(duckdb_path: Path) -> dict[str, set[str]]:
    import duckdb

    conn = duckdb.connect(str(duckdb_path), read_only=True)
    out: dict[str, set[str]] = {}
    for (t,) in conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_name LIKE 'stg_%' ORDER BY table_name"
    ).fetchall():
        base = t[4:].upper()
        cols = {str(row[0]).upper() for row in conn.execute(f"DESCRIBE {t}").fetchall()}
        out[base] = cols
    conn.close()
    return out


def run_build_process_flow(
    *,
    event_log_json: Path,
    output_dir: Path,
    duckdb_path: Path,
    sx3_candidates_json: Path | None,
) -> tuple[Path, Path]:
    """
    Gera process_flow em output_dir; persiste snapshot no DuckDB.
    Retorna (caminho json, caminho md).
    """
    if not event_log_json.exists():
        raise FileNotFoundError(event_log_json)
    if not duckdb_path.exists():
        raise FileNotFoundError(duckdb_path)

    events = load_event_log_json(event_log_json)
    cols = duckdb_staging_columns(duckdb_path)
    sx3 = load_sx3_candidates_json(sx3_candidates_json or (output_dir / "sx3_event_candidates.json"))

    payload = build_process_flow(events, duckdb_columns_by_table=cols, sx3_candidate_rows=sx3)
    jpath, mpath = write_process_flow_artifacts(payload, output_dir)

    import duckdb

    conn = duckdb.connect(str(duckdb_path), read_only=False)
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
    conn.close()

    return jpath, mpath


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gera fluxo de processo + Mermaid a partir do event log candidato.")
    p.add_argument("--input", type=Path, required=True, help="event_log_candidates.json")
    p.add_argument(
        "--output",
        "-o",
        "--output-dir",
        type=Path,
        dest="output_dir",
        default=Path("data/outputs/sx3_semantic"),
    )
    p.add_argument("--duckdb-path", type=Path, default=None)
    p.add_argument(
        "--sx3-candidates",
        type=Path,
        default=None,
        help="sx3_event_candidates.json para recuperação de INVALID_EVENT.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    duckdb_path = args.duckdb_path or local_lab_config.DUCKDB_PATH
    try:
        jpath, mpath = run_build_process_flow(
            event_log_json=args.input,
            output_dir=args.output_dir,
            duckdb_path=duckdb_path,
            sx3_candidates_json=args.sx3_candidates,
        )
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        raise SystemExit(1) from e
    print(f"Fluxo gerado: {jpath}")
    print(f"Mermaid: {mpath}")
    print(f"DuckDB: {duckdb_path} (tabela process_flow_snapshot)")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
