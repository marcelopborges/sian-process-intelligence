"""
Fluxo de processo linear a partir de event_log_candidates (CP).

Ordenação alinhada à macro dbt `cp_event_order` (desempate estável).
Recuperação simples de INVALID_EVENT via colunas alternativas no DuckDB.
Geração de arestas e diagrama Mermaid (sem LLM).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ordem canônica (cp_event_order) + desempate quando order igual (ex.: PAGAMENTO vs BAIXA = 5)
_CP_ORDER: dict[str, tuple[int, int]] = {
    "TITULO_CRIADO": (1, 0),
    "TITULO_LIBERADO": (2, 0),
    "EVENTO_FINANCEIRO_GERADO": (3, 0),
    "LANCAMENTO_CONTABIL": (4, 0),
    "PAGAMENTO_REALIZADO": (5, 0),
    "BAIXA_SEM_SE5": (5, 1),
    "TITULO_CANCELADO": (7, 0),
}

# Colunas alternativas para recuperar event_time (tabela Protheus em maiúsculas)
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
    """Chave de ordenação: (ordem macro, desempate, nome)."""
    a = activity.strip().upper()
    if a in _CP_ORDER:
        o, tie = _CP_ORDER[a]
        return (o, tie, a)
    # Fallback: fase heurística + alfabético
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


def emoji_for_alignment(dbt_alignment: str) -> str:
    u = (dbt_alignment or "").upper()
    if "ALINHADO" in u and "CONFIANCA" not in u:
        return "🟢"
    if "BAIXA" in u and "CONFIANCA" in u:
        return "🔴"
    if "PARCIAL" in u or "MEDIA" in u:
        return "🟡"
    return "🟡"


def _safe_mermaid_id(activity: str, index: int) -> str:
    base = re.sub(r"[^A-Za-z0-9_]", "_", activity)[:40]
    return f"n{index}_{base}"


def recover_invalid_event(
    event: dict[str, Any],
    duckdb_columns_by_table: dict[str, set[str]],
    sx3_candidate_rows: list[dict[str, Any]] | None,
) -> tuple[dict[str, Any], bool]:
    """
    Tenta recuperar event_time para INVALID_EVENT.
    Retorna (evento_atualizado, recuperou).
    """
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


def sort_events_for_flow(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena atividades pelo critério canônico + fallback."""
    return sorted(events, key=lambda e: activity_sort_key(str(e.get("activity", ""))))


def build_edges(ordered_valid: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Cadeia linear: de[i] -> de[i+1] apenas para eventos OK com event_time."""
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


def build_mermaid(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
) -> str:
    """Diagrama flowchart LR com rótulos activity (table) emoji."""
    lines = ["flowchart LR"]
    id_by_activity: dict[str, str] = {}
    for i, n in enumerate(nodes):
        act = str(n.get("activity", ""))
        aid = _safe_mermaid_id(act, i)
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


@dataclass
class ProcessFlowPayload:
    """Saída consolidada para JSON / DuckDB."""

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
    """
    - Recupera INVALID_EVENT quando possível.
    - Ordena nós.
    - Separa não confiáveis (ainda INVALID ou sem event_time).
    - Monta arestas e Mermaid.
    """
    now = datetime.now(timezone.utc).isoformat()
    recovered: list[dict[str, Any]] = []
    unreliable: list[dict[str, Any]] = []

    for ev in events:
        e2, ok = recover_invalid_event(ev, duckdb_columns_by_table, sx3_candidate_rows)
        if ok:
            recovered.append(e2)
        else:
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
    d = asdict(p)
    return d


def write_process_flow_artifacts(
    payload: ProcessFlowPayload,
    out_dir: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jpath = out_dir / "process_flow.json"
    mpath = out_dir / "process_flow.md"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(payload_to_json_dict(payload), f, ensure_ascii=False, indent=2)
    with mpath.open("w", encoding="utf-8") as f:
        f.write("# Fluxo de processo (CP) — candidato SX3\n\n")
        f.write("Gerado automaticamente. Ordenação alinhada a `cp_event_order` (dbt).\n\n")
        f.write("```mermaid\n")
        f.write(payload.mermaid)
        f.write("\n```\n")
    return jpath, mpath


def load_event_log_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("event_log_candidates.json deve ser uma lista JSON.")
    return data


def load_sx3_candidates_json(path: Path | None) -> list[dict[str, Any]] | None:
    if path is None or not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return None
