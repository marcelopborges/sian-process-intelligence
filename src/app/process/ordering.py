"""
Ordenação de atividades e recuperação de event_time (cp_event_order / desempate).
"""
from __future__ import annotations

import re
from typing import Any

_CP_ORDER: dict[str, tuple[int, int]] = {
    "TITULO_CRIADO": (1, 0),
    "TITULO_LIBERADO": (2, 0),
    "EVENTO_FINANCEIRO_GERADO": (3, 0),
    "LANCAMENTO_CONTABIL": (4, 0),
    "PAGAMENTO_REALIZADO": (5, 0),
    "BAIXA_SEM_SE5": (5, 1),
    "TITULO_CANCELADO": (7, 0),
}

_RECOVERY_FALLBACKS: dict[str, list[tuple[str, str]]] = {
    "LANCAMENTO_CONTABIL": [
        ("FK2", "F2_DATA_LANCAMENTO"),
        ("FK2", "F2_DBALTERACAO"),
        ("FK2", "F2_DIACTB"),
    ],
    "EVENTO_FINANCEIRO_GERADO": [
        ("FK7", "F7_DATA_EVENTO"),
        ("FK7", "F7_DBALTERACAO"),
    ],
}


def activity_sort_key(activity: str) -> tuple[int, int, str]:
    a = activity.strip().upper()
    if a in _CP_ORDER:
        o, tie = _CP_ORDER[a]
        return (o, tie, a)
    phase, tie2 = _phase_fallback(a)
    return (90 + phase, tie2, a)


def _phase_fallback(activity: str) -> tuple[int, int]:
    u = activity.upper()
    if "CANCEL" in u:
        return (7, 0)
    if "PAGAMENTO" in u or "BAIXA" in u:
        return (5, 0)
    if "LANC" in u or "CONTABIL" in u:
        return (4, 0)
    if "EVENTO" in u and "FIN" in u:
        return (3, 0)
    if "LIBER" in u:
        return (2, 0)
    if "TITULO" in u or "CRIAD" in u or "EMISS" in u:
        return (1, 0)
    return (50, 0)


def sort_events_for_flow(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(events, key=lambda e: activity_sort_key(str(e.get("activity", ""))))


def build_edges(ordered_valid: list[dict[str, Any]]) -> list[dict[str, str]]:
    valid = [
        e
        for e in ordered_valid
        if e.get("event_status") == "OK" and isinstance(e.get("event_time"), dict)
    ]
    edges: list[dict[str, str]] = []
    for i in range(len(valid) - 1):
        a0 = str(valid[i].get("activity", ""))
        a1 = str(valid[i + 1].get("activity", ""))
        edges.append({"from": a0, "to": a1})
    return edges


def recover_invalid_event(
    event: dict[str, Any],
    duckdb_columns_by_table: dict[str, set[str]],
    sx3_candidate_rows: list[dict[str, Any]] | None,
) -> tuple[dict[str, Any], bool]:
    if event.get("event_status") != "INVALID_EVENT":
        return event, False

    activity = str(event.get("activity", "")).strip().upper()

    for table, col in _RECOVERY_FALLBACKS.get(activity, []):
        cols = duckdb_columns_by_table.get(table.upper(), set())
        if col.upper() in cols:
            out = dict(event)
            out["event_status"] = "OK"
            out["event_time"] = {"table": table.upper(), "column": col.upper()}
            out["recovery"] = "fallback_known_alternate"
            return out, True

    if sx3_candidate_rows:
        cands = [
            r
            for r in sx3_candidate_rows
            if str(r.get("activity", "")).strip().upper() == activity
            and str(r.get("column_role", "")).upper() == "EVENT_TIME"
        ]
        cands.sort(key=lambda r: -float(r.get("heuristic_score", 0.0) or 0.0))
        for r in cands:
            t = str(r.get("source_table", "")).strip().upper()
            c = str(r.get("source_column", "")).strip().upper()
            if c in duckdb_columns_by_table.get(t, set()):
                out = dict(event)
                out["event_status"] = "OK"
                out["event_time"] = {"table": t, "column": c}
                out["recovery"] = "from_sx3_event_time_candidate"
                return out, True

    return event, False


def safe_mermaid_id(activity: str, index: int) -> str:
    base = re.sub(r"[^A-Za-z0-9_]", "_", activity)[:40]
    return f"n{index}_{base}"
