"""Raiz do repositório e caminhos estáveis (independente de CWD)."""
from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Contém `config/`, `dbt/`, `src/app/`, etc."""
    return Path(__file__).resolve().parents[2]
