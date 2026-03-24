"""
Configuração compartilhada do pytest.

Adicione fixtures comuns aqui (ex.: event log de exemplo, mocks de BigQuery).
"""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_event_log_columns():
    """Colunas obrigatórias do event log (ADR-003)."""
    return ["case_id", "activity", "timestamp"]
