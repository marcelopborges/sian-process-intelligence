"""
Testes para app.core.schemas.
"""
from __future__ import annotations

from app.core.schemas import (
    ACTIVITIES_CP,
    ACTIVITY,
    CASE_ID,
    EVENT_ORDER,
    EVENT_TIMESTAMP_ADJUSTED,
    EVENT_TIMESTAMP_ORIGINAL,
    TIMESTAMP_CONFIABILIDADE,
    recommended_columns,
    required_columns,
)


def test_required_columns():
    cols = required_columns()
    assert CASE_ID in cols
    assert ACTIVITY in cols
    assert EVENT_TIMESTAMP_ADJUSTED in cols
    assert EVENT_TIMESTAMP_ORIGINAL in cols
    assert EVENT_ORDER in cols
    assert TIMESTAMP_CONFIABILIDADE in cols
    assert len(cols) == 6


def test_recommended_columns():
    cols = recommended_columns()
    assert len(cols) >= 1
    assert "resource" in cols or "activity_instance_id" in cols


def test_activities_cp():
    assert "TITULO_CRIADO" in ACTIVITIES_CP
    assert "BAIXA_SEM_SE5" in ACTIVITIES_CP
    assert "PAGAMENTO_REALIZADO" in ACTIVITIES_CP
    assert len(ACTIVITIES_CP) == 7
