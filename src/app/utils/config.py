"""
Carregamento de configuração a partir de variáveis de ambiente.

Usa python-dotenv para .env. Variáveis esperadas: ver .env.example.
"""
from __future__ import annotations

import os
from pathlib import Path


def get_env(key: str, default: str | None = None) -> str | None:
    """Retorna variável de ambiente; carrega .env se existir."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    return os.environ.get(key, default)


def bq_project_id() -> str | None:
    return get_env("BQ_PROJECT_ID")


def bq_dataset_analytics() -> str | None:
    return get_env("BQ_DATASET_ANALYTICS")


def process_output_dir() -> Path:
    """Diretório de saída para artefatos de process mining/simulação."""
    raw = get_env("PROCESS_OUTPUT_DIR", "./output")
    return Path(raw)
