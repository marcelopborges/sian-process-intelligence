from __future__ import annotations

from python.validation.process_flow import (
    build_edges,
    build_process_flow,
    emoji_for_alignment,
    recover_invalid_event,
    sort_events_for_flow,
)


def test_activity_sort_order_cp():
    ev = [
        {"activity": a}
        for a in ["PAGAMENTO_REALIZADO", "TITULO_CRIADO", "LANCAMENTO_CONTABIL"]
    ]
    out = [e["activity"] for e in sort_events_for_flow(ev)]
    assert out == ["TITULO_CRIADO", "LANCAMENTO_CONTABIL", "PAGAMENTO_REALIZADO"]


def test_edges_chain():
    ev = [
        {"activity": "A", "event_status": "OK", "event_time": {"table": "T", "column": "C"}},
        {"activity": "B", "event_status": "OK", "event_time": {"table": "T", "column": "D"}},
    ]
    e = build_edges(sort_events_for_flow(ev))
    assert e == [{"from": "A", "to": "B"}]


def test_emoji_alignment():
    assert "🟢" in emoji_for_alignment("ALINHADO")
    assert "🟡" in emoji_for_alignment("PARCIAL")
    assert "🔴" in emoji_for_alignment("BAIXA_CONFIANCA")


def test_recover_lancamento_with_fk2_columns():
    duck = {"FK2": {"F2_DATA_LANCAMENTO", "F2_DBALTERACAO"}}
    ev = {
        "activity": "LANCAMENTO_CONTABIL",
        "event_status": "INVALID_EVENT",
        "event_time": None,
    }
    out, ok = recover_invalid_event(ev, duck, None)
    assert ok is True
    assert out["event_status"] == "OK"
    assert out["event_time"]["column"] == "F2_DATA_LANCAMENTO"


def test_build_process_flow_payload():
    events = [
        {
            "activity": "TITULO_CRIADO",
            "event_status": "OK",
            "event_time": {"table": "SE2", "column": "E2_EMISSAO"},
            "confidence": "ALTA",
            "dbt_alignment": "ALINHADO",
            "source_tables": ["SE2"],
        },
        {
            "activity": "PAGAMENTO_REALIZADO",
            "event_status": "OK",
            "event_time": {"table": "SE5", "column": "E5_DATA_PAGAMENTO"},
            "confidence": "MEDIA",
            "dbt_alignment": "PARCIAL",
            "source_tables": ["SE5"],
        },
    ]
    p = build_process_flow(events, duckdb_columns_by_table={"SE2": {"E2_EMISSAO"}, "SE5": {"E5_DATA_PAGAMENTO"}})
    assert len(p.edges) == 1
    assert p.edges[0]["from"] == "TITULO_CRIADO"
    assert "flowchart LR" in p.mermaid
