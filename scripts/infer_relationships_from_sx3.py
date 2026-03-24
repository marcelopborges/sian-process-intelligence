#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _bootstrap import ensure_src_on_path  # noqa: E402

ensure_src_on_path()

from app.lab import config as local_lab_config  # noqa: E402


def _duckdb_tables(conn) -> list[tuple[str, list[str]]]:
    tables = conn.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='main'
        ORDER BY table_name
        """
    ).fetchall()
    out: list[tuple[str, list[str]]] = []
    for (t,) in tables:
        if not t.lower().startswith("stg_"):
            continue
        cols = [r[0] for r in conn.execute(f"DESCRIBE {t}").fetchall()]
        out.append((t, cols))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Inferir relacionamentos a partir do SX3 (heurística).")
    parser.add_argument(
        "--sx3",
        "--sx3-csv",
        type=Path,
        dest="sx3_csv",
        default=Path("data/others/SX3010_202603231122.csv"),
        help="Caminho do SX3 CSV exportado (ex.: SX3010_....csv).",
    )
    parser.add_argument(
        "--duckdb-path",
        type=Path,
        default=local_lab_config.DUCKDB_PATH,
        help="DuckDB local (laboratório).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("data/outputs/sx3_semantic"),
        help="Diretório de saída para JSON/Markdown.",
    )
    parser.add_argument("--min-confidence", type=float, default=0.6)
    args = parser.parse_args()

    if not args.sx3_csv.exists():
        raise FileNotFoundError(f"SX3 CSV não encontrado: {args.sx3_csv}")
    if not args.duckdb_path.exists():
        raise FileNotFoundError(f"DuckDB não encontrado: {args.duckdb_path}")

    try:
        import duckdb
    except ImportError as e:
        raise SystemExit("duckdb não instalado. Instale com: pip install duckdb") from e

    from app.discovery.relationship_inferer import infer_relationship_suggestions
    from app.discovery.sx3_loader import build_sx3_metadata, load_sx3_csv

    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sx3_df = load_sx3_csv(args.sx3_csv)
    sx3_meta = build_sx3_metadata(sx3_df)

    conn = duckdb.connect(str(args.duckdb_path), read_only=False)

    duckdb_tables = _duckdb_tables(conn)
    if not duckdb_tables:
        print("Nenhuma tabela stg_* encontrada no DuckDB.")
        conn.close()
        return

    suggestions = infer_relationship_suggestions(sx3_meta=sx3_meta, duckdb_tables=duckdb_tables)
    suggestions = [s for s in suggestions if s.confidence >= args.min_confidence]

    # Persistência no DuckDB (útil para inspeção e auditoria)
    conn.execute(
        """
        CREATE OR REPLACE TABLE sx3_relationship_suggestions (
          suggestion_id VARCHAR,
          source_table VARCHAR,
          target_table VARCHAR,
          source_column VARCHAR,
          target_column VARCHAR,
          confidence DOUBLE,
          reason VARCHAR,
          sx3_source_f3 VARCHAR,
          sx3_target_f3 VARCHAR,
          created_at_utc VARCHAR
        )
        """
    )

    if suggestions:
        # Inserção batch via executemany
        conn.executemany(
            """
            INSERT INTO sx3_relationship_suggestions
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    s.suggestion_id,
                    s.source_table,
                    s.target_table,
                    s.source_column,
                    s.target_column,
                    float(s.confidence),
                    s.reason,
                    s.sx3_source_f3,
                    s.sx3_target_f3,
                    s.created_at_utc,
                )
                for s in suggestions
            ],
        )

    # JSON
    json_path = out_dir / "sx3_relationship_suggestions.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump([s.__dict__ for s in suggestions], f, ensure_ascii=False, indent=2)

    # Markdown (top N)
    md_path = out_dir / "sx3_relationship_suggestions.md"
    top = sorted(suggestions, key=lambda x: -x.confidence)[:50]
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Sugestões de relacionamento (SX3)\\n\\n")
        f.write(f"- total_sugestoes: {len(suggestions)}\\n")
        f.write("\\n| confidence | source_table | source_column | target_table | target_column | reason |\\n")
        f.write("|---:|---|---|---|---|---|\\n")
        for s in top:
            f.write(
                f"| {s.confidence:.3f} | {s.source_table} | {s.source_column} | {s.target_table} | {s.target_column} | {s.reason} |\\n"
            )

    print(f"Inferência concluída. Sugestões: {len(suggestions)}")
    print(f"DuckDB: {args.duckdb_path} (tabela sx3_relationship_suggestions)")
    print(f"Arquivos: {json_path} e {md_path}")

    conn.close()


if __name__ == "__main__":
    main()

