"""Geração de diagramas Mermaid a partir de nós e arestas."""
from __future__ import annotations

from typing import Any

from app.process.ordering import safe_mermaid_id


def emoji_for_alignment(dbt_alignment: str) -> str:
    u = (dbt_alignment or "").upper()
    if "ALINHADO" in u and "CONFIANCA" not in u:
        return "🟢"
    if "BAIXA" in u and "CONFIANCA" in u:
        return "🔴"
    if "PARCIAL" in u or "MEDIA" in u:
        return "🟡"
    return "🟡"


def build_mermaid(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
) -> str:
    lines = ["flowchart LR"]
    id_by_activity: dict[str, str] = {}
    for i, n in enumerate(nodes):
        act = str(n.get("activity", ""))
        aid = safe_mermaid_id(act, i)
        id_by_activity[act] = aid
        et = n.get("event_time") or {}
        tbl = et.get("table", "?") if isinstance(et, dict) else "?"
        emo = emoji_for_alignment(str(n.get("dbt_alignment", "")))
        label = f"{act} ({tbl}) {emo}"
        safe = label.replace('"', "'")
        lines.append(f'  {aid}["{safe}"]')

    for e in edges:
        f, t = e.get("from", ""), e.get("to", "")
        if f in id_by_activity and t in id_by_activity:
            lines.append(f"  {id_by_activity[f]} --> {id_by_activity[t]}")

    return "\n".join(lines)
