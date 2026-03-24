"""
Extrai subconjuntos do BigQuery para arquivos Parquet locais.

Uso: python -m python.local_lab.extract_bigquery_to_parquet

Requisitos: google-cloud-bigquery, pyarrow (ou pandas com to_parquet).
Config: python/local_lab/config.py e variáveis de ambiente (BQ_PROJECT_ID, etc.).
HYPOTHESIS: nomes de tabelas e colunas devem ser validados no ambiente real.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Garantir que o repo root está no path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.local_lab import config


def _get_client():
    """Retorna cliente BigQuery. Falha com mensagem clara se não configurado."""
    try:
        from google.cloud import bigquery
    except ImportError:
        print("ERRO: google-cloud-bigquery não instalado. pip install google-cloud-bigquery pyarrow")
        sys.exit(1)
    return bigquery.Client(project=config.BQ_CLIENT_PROJECT or None)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _extract_table(client, project: str, dataset: str, table: str, limit: int, date_filter: str) -> str:
    """
    Executa SELECT * FROM project.dataset.table com filtro opcional.
    limit=0: sem LIMIT (extrai tudo); limit>0: adiciona LIMIT n.
    Retorna a query SQL usada.
    """
    full_table = f"`{project}`.{dataset}.{table}"
    where = f" WHERE {date_filter}" if date_filter else ""
    limit_clause = f" LIMIT {limit}" if limit > 0 else ""
    sql = f"SELECT * FROM {full_table}{where}{limit_clause}"
    return sql


def extract_se2() -> None:
    """Extrai SE2 (SIAN_SE2, títulos a pagar) para data/extracts/se2.parquet."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_SE2, config.BQ_DATASET_SE2, config.BQ_TABLE_SE2,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    # TODO/HYPOTHESIS: colunas reais podem diferir; considerar alias para e2_filial, e2_prefixo, etc.
    print(f"Extraindo SE2: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        # Normalizar nomes para minúsculo com prefixo e2_ se vierem como E2_* do BQ
        if not df.empty and any(str(c).upper().startswith("E2_") for c in df.columns):
            df.columns = [c.lower() if str(c).upper().startswith("E2_") else c for c in df.columns]
        df.to_parquet(config.PARQUET_SE2, index=False)
        print(f"  -> {config.PARQUET_SE2} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_fk7() -> None:
    """Extrai FK7 para data/extracts/fk7.parquet (projeto financeiro, silver)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_FK7, config.BQ_DATASET_FK7, config.BQ_TABLE_FK7,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo FK7: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        if not df.empty and any(str(c).upper().startswith("F7_") for c in df.columns):
            df.columns = [c.lower() if str(c).upper().startswith("F7_") else c for c in df.columns]
        df.to_parquet(config.PARQUET_FK7, index=False)
        print(f"  -> {config.PARQUET_FK7} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_fk2() -> None:
    """Extrai FK2 para data/extracts/fk2.parquet (projeto financeiro, silver)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_FK2, config.BQ_DATASET_FK2, config.BQ_TABLE_FK2,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo FK2: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        if not df.empty and any(str(c).upper().startswith("F2_") for c in df.columns):
            df.columns = [c.lower() if str(c).upper().startswith("F2_") else c for c in df.columns]
        df.to_parquet(config.PARQUET_FK2, index=False)
        print(f"  -> {config.PARQUET_FK2} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_fk1() -> None:
    """Extrai FK1 para data/extracts/fk1.parquet (projeto financeiro, silver)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_FK1, config.BQ_DATASET_FK1, config.BQ_TABLE_FK1,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo FK1: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        df.to_parquet(config.PARQUET_FK1, index=False)
        print(f"  -> {config.PARQUET_FK1} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_fk5() -> None:
    """Extrai FK5 para data/extracts/fk5.parquet (projeto financeiro, silver)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_FK5, config.BQ_DATASET_FK5, config.BQ_TABLE_FK5,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo FK5: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        df.to_parquet(config.PARQUET_FK5, index=False)
        print(f"  -> {config.PARQUET_FK5} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_fk6() -> None:
    """Extrai FK6 para data/extracts/fk6.parquet (projeto financeiro, silver)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_FK6, config.BQ_DATASET_FK6, config.BQ_TABLE_FK6,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo FK6: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        df.to_parquet(config.PARQUET_FK6, index=False)
        print(f"  -> {config.PARQUET_FK6} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def extract_se5() -> None:
    """Extrai SE5 para data/extracts/se5.parquet (projeto suprimentos, raw)."""
    client = _get_client()
    _ensure_dir(config.EXTRACTS_DIR)
    sql = _extract_table(
        client, config.BQ_PROJECT_SE5, config.BQ_DATASET_SE5, config.BQ_TABLE_SE5,
        config.EXTRACT_ROW_LIMIT, config.EXTRACT_DATE_FILTER,
    )
    print(f"Extraindo SE5: {sql[:80]}...")
    try:
        df = client.query(sql).to_dataframe()
        if not df.empty and any(str(c).upper().startswith("E5_") for c in df.columns):
            df.columns = [c.lower() if str(c).upper().startswith("E5_") else c for c in df.columns]
        df.to_parquet(config.PARQUET_SE5, index=False)
        print(f"  -> {config.PARQUET_SE5} ({len(df)} linhas)")
    except Exception as e:
        print(f"  ERRO: {e}")
        raise


def main() -> None:
    print("=== Extração BigQuery -> Parquet (laboratório local) ===\n")
    extract_se2()
    extract_fk7()
    extract_fk2()
    extract_fk1()
    extract_fk5()
    extract_fk6()
    extract_se5()
    print("\nExtração concluída.")


if __name__ == "__main__":
    main()
