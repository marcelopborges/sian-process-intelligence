#!/usr/bin/env python3
"""
Gera process_flow.json + process_flow.md a partir de event_log_candidates.json.

Uso (raiz do repo):
  python scripts/build_process_flow.py \\
    --input output/sx3_semantic/event_log_candidates.json \\
    --duckdb-path local/process_intelligence.duckdb \\
    -o output/sx3_semantic

Opcional: --sx3-candidates output/sx3_semantic/sx3_event_candidates.json (recuperação INVALID_EVENT).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.local_lab import config as local_lab_config
from python.validation.process_flow import (
    build_process_flow,
    load_event_log_json,
    load_sx3_candidates_json,
    payload_to_json_dict,
    write_process_flow_artifacts,
)


def _duckdb_columns(duckdb_path: Path) -> dict[str, set[str]]:
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


def main() -> None:
    p = argparse.ArgumentParser(description="Gera fluxo de processo + Mermaid a partir do event log candidato.")
    p.add_argument("--input", type=Path, required=True, help="event_log_candidates.json")
    p.add_argument("--duckdb-path", type=Path, default=None)
    p.add_argument("-o", "--output-dir", type=Path, default=Path("output/sx3_semantic"))
    p.add_argument(
        "--sx3-candidates",
        type=Path,
        default=None,
        help="sx3_event_candidates.json para recuperação de INVALID_EVENT.",
    )
    args = p.parse_args()

    duckdb_path = args.duckdb_path or local_lab_config.DUCKDB_PATH
    if not args.input.exists():
        raise FileNotFoundError(args.input)
    if not duckdb_path.exists():
        raise FileNotFoundError(duckdb_path)

    events = load_event_log_json(args.input)
    cols = _duckdb_columns(duckdb_path)
    sx3 = load_sx3_candidates_json(args.sx3_candidates or (args.output_dir / "sx3_event_candidates.json"))

    payload = build_process_flow(events, duckdb_columns_by_table=cols, sx3_candidate_rows=sx3)
    jpath, mpath = write_process_flow_artifacts(payload, args.output_dir)

    # DuckDB opcional
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

    print(f"Fluxo gerado: {jpath}")
    print(f"Mermaid: {mpath}")
    print(f"DuckDB: {duckdb_path} (tabela process_flow_snapshot)")


if __name__ == "__main__":
    main()
