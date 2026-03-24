"""
Materializa cp_event_log_semantic no DuckDB a partir do SQL local e exporta Parquet.

Uso: python -m app.lab.materialize_cp_event_log_semantic

Requisitos:
- DuckDB já populado e com cp_event_log materializado (via materialize_cp_event_log).
"""
from __future__ import annotations

import sys

from app.lab import config


def main() -> None:
    print("=== Materialização cp_event_log_semantic (DuckDB) ===\n")

    if not config.SQL_CP_EVENT_LOG_SEMANTIC.exists():
        print(f"ERRO: SQL não encontrado: {config.SQL_CP_EVENT_LOG_SEMANTIC}")
        sys.exit(1)
    if not config.DUCKDB_PATH.exists():
        print(f"ERRO: DuckDB não encontrado. Execute antes: load_parquet_to_duckdb. Path: {config.DUCKDB_PATH}")
        sys.exit(1)

    try:
        import duckdb
    except ImportError:
        print("ERRO: duckdb não instalado. pip install duckdb")
        sys.exit(1)

    sql = config.SQL_CP_EVENT_LOG_SEMANTIC.read_text(encoding="utf-8")
    conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=False)

    # A camada semântica nasce do que já está materializado (cp_event_log).
    conn.execute("CREATE OR REPLACE TABLE cp_event_log_semantic AS " + sql)
    n = conn.execute("SELECT COUNT(*) FROM cp_event_log_semantic").fetchone()[0]
    print(f"  cp_event_log_semantic: {n} linhas")

    config.MARTS_DIR.mkdir(parents=True, exist_ok=True)
    out_parquet = config.MARTS_DIR / "cp_event_log_semantic.parquet"
    conn.execute(f"COPY cp_event_log_semantic TO '{out_parquet.resolve().as_posix()}' (FORMAT PARQUET)")
    print(f"  Exportado: {out_parquet}")

    conn.close()
    print("Concluído.")


if __name__ == "__main__":
    main()

