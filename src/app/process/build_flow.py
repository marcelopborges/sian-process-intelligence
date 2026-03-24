"""
Monta o payload do fluxo de processo (nós, arestas, não confiáveis, Mermaid).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.presentation.generate_mermaid import build_mermaid
from app.process.ordering import (
    build_edges,
    recover_invalid_event,
    sort_events_for_flow,
)


@dataclass
class ProcessFlowPayload:
    generated_at_utc: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, str]]
    unreliable_events: list[dict[str, Any]]
    mermaid: str
    meta: dict[str, Any] = field(default_factory=dict)


def build_process_flow(
    events: list[dict[str, Any]],
    *,
    duckdb_columns_by_table: dict[str, set[str]],
    sx3_candidate_rows: list[dict[str, Any]] | None = None,
) -> ProcessFlowPayload:
    now = datetime.now(UTC).isoformat()
    recovered: list[dict[str, Any]] = []
    unreliable: list[dict[str, Any]] = []

    for ev in events:
        e2, _ok = recover_invalid_event(ev, duckdb_columns_by_table, sx3_candidate_rows)
        recovered.append(e2)

    ordered = sort_events_for_flow(recovered)

    for e in ordered:
        if e.get("event_status") == "INVALID_EVENT" or not e.get("event_time"):
            unreliable.append(
                {
                    "activity": e.get("activity"),
                    "event_status": e.get("event_status"),
                    "reason": "sem_event_time_apos_recuperacao",
                    "dbt_alignment": e.get("dbt_alignment"),
                }
            )

    main_nodes = [
        n
        for n in ordered
        if n.get("event_status") == "OK" and isinstance(n.get("event_time"), dict)
    ]

    edges = build_edges(ordered)

    mermaid_nodes = [
        {
            "activity": n.get("activity"),
            "event_time": n.get("event_time"),
            "dbt_alignment": n.get("dbt_alignment"),
        }
        for n in main_nodes
    ]
    mermaid = build_mermaid(mermaid_nodes, edges)

    full_nodes = []
    for n in ordered:
        et = n.get("event_time") if isinstance(n.get("event_time"), dict) else None
        full_nodes.append(
            {
                "activity": n.get("activity"),
                "event_status": n.get("event_status"),
                "event_time": et,
                "confidence": n.get("confidence"),
                "dbt_alignment": n.get("dbt_alignment"),
                "source_tables": n.get("source_tables"),
                "recovery": n.get("recovery"),
            }
        )

    return ProcessFlowPayload(
        generated_at_utc=now,
        nodes=full_nodes,
        edges=edges,
        unreliable_events=unreliable,
        mermaid=mermaid,
        meta={
            "ordering": "cp_event_order_macro_plus_tiebreak",
            "nodes_in_diagram": len(main_nodes),
        },
    )


def payload_to_json_dict(p: ProcessFlowPayload) -> dict[str, Any]:
    return asdict(p)
