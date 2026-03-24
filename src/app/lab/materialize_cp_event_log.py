"""
Materializa cp_event_log no DuckDB a partir do SQL local e opcionalmente exporta Parquet.

Uso: python -m app.lab.materialize_cp_event_log

Requisitos: DuckDB já populado com stg_se2, stg_fk7, stg_fk2, stg_se5 (via load_parquet_to_duckdb).
"""
from __future__ import annotations

import sys

from app.lab import config


def main() -> None:
    print("=== Materialização cp_event_log (DuckDB) ===\n")

    if not config.SQL_CP_EVENT_LOG.exists():
        print(f"ERRO: SQL não encontrado: {config.SQL_CP_EVENT_LOG}")
        sys.exit(1)
    if not config.DUCKDB_PATH.exists():
        print(f"ERRO: DuckDB não encontrado. Execute antes: load_parquet_to_duckdb. Path: {config.DUCKDB_PATH}")
        sys.exit(1)

    try:
        import duckdb
    except ImportError:
        print("ERRO: duckdb não instalado. pip install duckdb")
        sys.exit(1)

    sql = config.SQL_CP_EVENT_LOG.read_text(encoding="utf-8")
    conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=False)
    conn.execute("CREATE OR REPLACE TABLE cp_event_log AS " + sql)
    n = conn.execute("SELECT COUNT(*) FROM cp_event_log").fetchone()[0]
    print(f"  cp_event_log: {n} linhas")

    config.MARTS_DIR.mkdir(parents=True, exist_ok=True)
    out_parquet = config.MARTS_DIR / "cp_event_log.parquet"
    conn.execute(f"COPY cp_event_log TO '{out_parquet.resolve().as_posix()}' (FORMAT PARQUET)")
    print(f"  Exportado: {out_parquet}")

    conn.close()
    print("Concluído.")


if __name__ == "__main__":
    main()
