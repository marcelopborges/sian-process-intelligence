"""
Carrega Parquets locais em DuckDB (stg_se2, stg_fk7, stg_fk2, stg_se5; opcional: stg_fk1, stg_fk5, stg_fk6).

Uso: python -m app.lab.load_parquet_to_duckdb

Requisitos: duckdb. Falha se os 4 Parquets obrigatórios não existirem; FK1/FK5/FK6 são opcionais.
"""
from __future__ import annotations

import sys
from pathlib import Path

from app.lab import config


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print("=== Carga Parquet -> DuckDB (laboratório local) ===\n")

    obrigatorios = [
        (config.PARQUET_SE2, "stg_se2"),
        (config.PARQUET_FK7, "stg_fk7"),
        (config.PARQUET_FK2, "stg_fk2"),
        (config.PARQUET_SE5, "stg_se5"),
    ]
    opcionais = [
        (config.PARQUET_FK1, "stg_fk1"),
        (config.PARQUET_FK5, "stg_fk5"),
        (config.PARQUET_FK6, "stg_fk6"),
    ]
    missing = [p for p, _ in obrigatorios if not p.exists()]
    if missing:
        print("ERRO: Arquivos Parquet não encontrados. Execute antes a extração BigQuery -> Parquet.")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    try:
        import duckdb
    except ImportError:
        print("ERRO: duckdb não instalado. pip install duckdb")
        sys.exit(1)

    _ensure_dir(config.LOCAL_DB_DIR)
    conn = duckdb.connect(str(config.DUCKDB_PATH))

    for parquet_path, table_name in obrigatorios:
        path_str = parquet_path.resolve().as_posix()
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{path_str}')")
        n = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  {table_name}: {n} linhas (de {parquet_path.name})")

    for parquet_path, table_name in opcionais:
        if not parquet_path.exists():
            print(f"  {table_name}: (omitido — {parquet_path.name} não encontrado)")
            continue
        path_str = parquet_path.resolve().as_posix()
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{path_str}')")
        n = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  {table_name}: {n} linhas (de {parquet_path.name})")

    conn.close()
    print(f"\nDuckDB: {config.DUCKDB_PATH}")
    print("Carga concluída.")


if __name__ == "__main__":
    main()
