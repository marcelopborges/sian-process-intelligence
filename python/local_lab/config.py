"""
Configuração do laboratório local (BigQuery → Parquet → DuckDB).

Variáveis podem vir de ambiente ou ser sobrescritas. Não usar valores definitivos
sem validação do schema real do ambiente.
"""
from __future__ import annotations

import os
from pathlib import Path

# Raiz do repositório (assumindo execução a partir da raiz ou scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# --- Caminhos locais ---
DATA_DIR = Path(os.environ.get("LOCAL_LAB_DATA_DIR", str(REPO_ROOT / "data")))
EXTRACTS_DIR = DATA_DIR / "extracts"
MARTS_DIR = DATA_DIR / "marts"
LOCAL_DB_DIR = Path(os.environ.get("LOCAL_LAB_DB_DIR", str(REPO_ROOT / "local")))
DUCKDB_PATH = LOCAL_DB_DIR / "process_intelligence.duckdb"

# --- BigQuery: projeto/dataset únicos (fallback) ou por tabela ---
BQ_PROJECT = os.environ.get("BQ_PROJECT_ID", "")
BQ_DATASET = os.environ.get("BQ_DATASET_RAW", "")

# Por tabela (SIAN: suprimentos vs financeiro). Fallback = BQ_PROJECT_ID / BQ_DATASET_RAW quando setados.
def _bq_project(table: str) -> str:
    key = f"BQ_PROJECT_{table}"
    return os.environ.get(key) or os.environ.get(
        "BQ_PROJECT_ID",
        {
            "SE2": "gcp-sian-proj-suprimentos",
            "SE5": "gcp-sian-proj-suprimentos",
            "FK7": "gcp-sian-proj-financeiro",
            "FK2": "gcp-sian-proj-financeiro",
            "FK1": "gcp-sian-proj-financeiro",
            "FK5": "gcp-sian-proj-financeiro",
            "FK6": "gcp-sian-proj-financeiro",
        }[table],
    )

def _bq_dataset(table: str) -> str:
    key = f"BQ_DATASET_{table}"
    return os.environ.get(key) or os.environ.get(
        "BQ_DATASET_RAW",
        {
            "SE2": "silver",
            "FK7": "silver",
            "FK2": "silver",
            "FK1": "silver",
            "FK5": "silver",
            "FK6": "silver",
            "SE5": "raw",
        }[table],
    )

BQ_PROJECT_SE2 = _bq_project("SE2")
BQ_DATASET_SE2 = _bq_dataset("SE2")
BQ_TABLE_SE2 = os.environ.get("BQ_TABLE_SE2", "SIAN_SE2")
BQ_PROJECT_FK7 = _bq_project("FK7")
BQ_DATASET_FK7 = _bq_dataset("FK7")
BQ_TABLE_FK7 = os.environ.get("BQ_TABLE_FK7", "FK7")
BQ_PROJECT_FK2 = _bq_project("FK2")
BQ_DATASET_FK2 = _bq_dataset("FK2")
BQ_TABLE_FK2 = os.environ.get("BQ_TABLE_FK2", "FK2")
BQ_PROJECT_FK1 = _bq_project("FK1")
BQ_DATASET_FK1 = _bq_dataset("FK1")
BQ_TABLE_FK1 = os.environ.get("BQ_TABLE_FK1", "FK1")
BQ_PROJECT_FK5 = _bq_project("FK5")
BQ_DATASET_FK5 = _bq_dataset("FK5")
BQ_TABLE_FK5 = os.environ.get("BQ_TABLE_FK5", "FK5")
BQ_PROJECT_FK6 = _bq_project("FK6")
BQ_DATASET_FK6 = _bq_dataset("FK6")
BQ_TABLE_FK6 = os.environ.get("BQ_TABLE_FK6", "FK6")
BQ_PROJECT_SE5 = _bq_project("SE5")
BQ_DATASET_SE5 = _bq_dataset("SE5")
BQ_TABLE_SE5 = os.environ.get("BQ_TABLE_SE5", "SE5")

# Projeto usado pelo cliente BigQuery (billing); qualquer um dos projetos serve
BQ_CLIENT_PROJECT = os.environ.get("BQ_PROJECT_ID") or BQ_PROJECT_SE2

# --- Limites de extração: 0 = sem limite (extrair tudo); >0 = LIMIT n ---
EXTRACT_ROW_LIMIT = int(os.environ.get("LOCAL_LAB_EXTRACT_LIMIT", "0"))
# Filtro opcional por data (coluna a definir conforme schema real). Ex.: "E2_EMISSAO >= '2024-01-01'"
EXTRACT_DATE_FILTER = os.environ.get("LOCAL_LAB_DATE_FILTER", "")

# --- Arquivos Parquet esperados após extração ---
PARQUET_SE2 = EXTRACTS_DIR / "se2.parquet"
PARQUET_FK7 = EXTRACTS_DIR / "fk7.parquet"
PARQUET_FK2 = EXTRACTS_DIR / "fk2.parquet"
PARQUET_FK1 = EXTRACTS_DIR / "fk1.parquet"
PARQUET_FK5 = EXTRACTS_DIR / "fk5.parquet"
PARQUET_FK6 = EXTRACTS_DIR / "fk6.parquet"
PARQUET_SE5 = EXTRACTS_DIR / "se5.parquet"

# --- SQL marts (path relativo ao repo) ---
SQL_MARTS_DIR = REPO_ROOT / "sql" / "marts"
SQL_CP_CASE_BASE = SQL_MARTS_DIR / "cp_case_base.sql"
SQL_CP_EVENT_LOG = SQL_MARTS_DIR / "cp_event_log.sql"
SQL_CP_EVENT_LOG_SEMANTIC = SQL_MARTS_DIR / "cp_event_log_semantic.sql"
