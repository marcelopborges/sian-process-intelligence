from __future__ import annotations

from dataclasses import dataclass

from python.validation.event_log_builder import (
    aggregate_dbt_alignment,
    build_event_log_records,
    compute_event_confidence,
)


@dataclass
class _Row:
    activity: str
    source_table: str
    source_column: str
    column_role: str
    heuristic_score: float
    dbt_classification: str


def test_aggregate_dbt_priority():
    assert aggregate_dbt_alignment(["EXISTE_NA_FONTE_NAO_USADO", "ALINHADO_MART"]) == "ALINHADO"
    assert aggregate_dbt_alignment(["SEM_COLUNA_NA_FONTE", "ALINHADO_MART"]) == "ALINHADO"
    assert aggregate_dbt_alignment(["SEM_COLUNA_NA_FONTE", "EXISTE_NA_FONTE_NAO_USADO"]) == (
        "BAIXA_CONFIANCA"
    )


def test_compute_event_confidence():
    assert compute_event_confidence(0.80, "ALINHADO_MART") == "ALTA"
    assert compute_event_confidence(0.70, "ALINHADO_MART") == "MEDIA"
    assert compute_event_confidence(0.70, "EXISTE_NA_FONTE_NAO_USADO") == "MEDIA"
    assert compute_event_confidence(0.70, "SEM_COLUNA_NA_FONTE") == "BAIXA"


def test_build_one_activity_picks_best_event_time():
    rows = [
        _Row("PAGAMENTO_REALIZADO", "SE5", "E5_VALOR_PAGO", "ATTRIBUTE", 0.9, "ALINHADO_MART"),
        _Row("PAGAMENTO_REALIZADO", "SE5", "E5_DATA_PAGAMENTO", "EVENT_TIME", 0.85, "ALINHADO_MART"),
        _Row("PAGAMENTO_REALIZADO", "SE5", "E5_BANCO", "ATTRIBUTE", 0.82, "ALINHADO_MART"),
    ]
    out = build_event_log_records(rows, top_attributes_per_event=10)
    assert len(out) == 1
    ev = out[0]
    assert ev.activity == "PAGAMENTO_REALIZADO"
    assert ev.event_status == "OK"
    assert ev.event_time == {"table": "SE5", "column": "E5_DATA_PAGAMENTO"}
    cols = {a["column"] for a in ev.attributes}
    assert "E5_VALOR_PAGO" in cols
    assert "E5_BANCO" in cols
