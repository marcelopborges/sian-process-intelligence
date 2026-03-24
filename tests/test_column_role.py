from __future__ import annotations

from python.validation.column_role import classify_column_role


def test_event_time_patterns():
    assert classify_column_role("E2_EMISSAO") == "EVENT_TIME"
    assert classify_column_role("F7_DBALTERACAO") == "EVENT_TIME"
    assert classify_column_role("E5_DATA_PAGAMENTO") == "EVENT_TIME"


def test_attribute_patterns():
    assert classify_column_role("E5_VALOR_PAGO") == "ATTRIBUTE"
    assert classify_column_role("E5_VALOR") == "ATTRIBUTE"


def test_identifier():
    assert classify_column_role("E2_PREFIXO") == "IDENTIFIER"
    assert classify_column_role("E2_NUM") == "IDENTIFIER"


def test_status():
    assert classify_column_role("E2_STATUS") == "STATUS"
