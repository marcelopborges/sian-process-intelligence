"""
Agrega candidatos enriquecidos (por coluna) em 1 registro por activity — event log candidato.

Não infere joins; não usa LLM.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class EventLogCandidate:
    """Um evento agregado por activity (modelagem de processo)."""

    activity: str
    event_status: str  # OK | INVALID_EVENT
    event_time: dict[str, str] | None
    attributes: list[dict[str, str]]
    source_tables: list[str]
    confidence: str  # ALTA | MEDIA | BAIXA
    dbt_alignment: str  # ALINHADO | PARCIAL | BAIXA_CONFIANCA


def _partial_dbt(dbt_cls: str) -> bool:
    return dbt_cls in (
        "CANDIDATO_ALTERNATIVO",
        "CONFLITA_COM_REGRA_ATUAL",
        "REQUER_VALIDACAO_NEGOCIO",
        "EXISTE_NA_FONTE_NAO_USADO",
    )


def compute_event_confidence(heuristic_score: float, dbt_classification: str) -> str:
    """
    Confiança do evento a partir do timestamp escolhido (score + classificação dbt).
    """
    if dbt_classification == "SEM_COLUNA_NA_FONTE":
        return "BAIXA"
    if heuristic_score >= 0.75 and dbt_classification == "ALINHADO_MART":
        return "ALTA"
    if heuristic_score >= 0.65 and _partial_dbt(dbt_classification):
        return "MEDIA"
    if heuristic_score >= 0.65 and dbt_classification == "ALINHADO_MART":
        return "MEDIA"
    if heuristic_score >= 0.65:
        return "MEDIA"
    return "BAIXA"


def aggregate_dbt_alignment(classifications: list[str]) -> str:
    """
    Agrega classificações dbt dos candidatos que compõem o evento (time + atributos).

    Prioridade: ALINHADO_MART → ALINHADO; SEM_COLUNA → BAIXA_CONFIANCA;
    EXISTE_NA_FONTE_NAO_USADO → PARCIAL; demais → PARCIAL.
    """
    if any(x == "ALINHADO_MART" for x in classifications):
        return "ALINHADO"
    if any(x == "SEM_COLUNA_NA_FONTE" for x in classifications):
        return "BAIXA_CONFIANCA"
    if any(x == "EXISTE_NA_FONTE_NAO_USADO" for x in classifications):
        return "PARCIAL"
    return "PARCIAL"


def _col_key(table: str, column: str) -> tuple[str, str]:
    return table.upper(), column.upper()


def select_event_time_row(rows: list[Any]) -> Any | None:
    """
    Entre linhas com column_role EVENT_TIME, escolhe a de maior heuristic_score.
    """
    et = [r for r in rows if getattr(r, "column_role", None) == "EVENT_TIME"]
    if not et:
        return None
    return sorted(et, key=lambda r: -float(getattr(r, "heuristic_score", 0.0)))[0]


def select_attribute_rows(
    rows: list[Any],
    event_time_row: Any | None,
    top_attributes: int | None,
) -> list[Any]:
    """
    Colunas com papel ATTRIBUTE; exclui a mesma (table,column) do event_time.
    Ordena por heuristic_score desc; opcionalmente limita quantidade.
    """
    et_key = None
    if event_time_row is not None:
        et_key = _col_key(
            str(getattr(event_time_row, "source_table", "")),
            str(getattr(event_time_row, "source_column", "")),
        )

    attr = [r for r in rows if getattr(r, "column_role", None) == "ATTRIBUTE"]
    out: list[Any] = []
    seen: set[tuple[str, str]] = set()
    if et_key:
        seen.add(et_key)
    for r in sorted(attr, key=lambda x: -float(getattr(x, "heuristic_score", 0.0))):
        k = _col_key(str(getattr(r, "source_table", "")), str(getattr(r, "source_column", "")))
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
        if top_attributes is not None and top_attributes > 0 and len(out) >= top_attributes:
            break
    return out


def build_event_log_records(
    enriched_rows: list[Any],
    *,
    top_attributes_per_event: int | None = None,
) -> list[EventLogCandidate]:
    """
    Agrega por `activity`: 1 registro por atividade com event_time + attributes.

    `enriched_rows`: objetos com activity, source_table, source_column, heuristic_score,
    dbt_classification, column_role.
    """
    by_act: dict[str, list[Any]] = {}
    for r in enriched_rows:
        act = str(getattr(r, "activity", "") or "").strip()
        if not act:
            continue
        by_act.setdefault(act, []).append(r)

    out: list[EventLogCandidate] = []
    for activity in sorted(by_act.keys()):
        rows = by_act[activity]
        et_row = select_event_time_row(rows)
        attr_rows = select_attribute_rows(rows, et_row, top_attributes_per_event)

        if et_row is None:
            # INVALID_EVENT — sem coluna EVENT_TIME; mantém atributos para debug
            attr_rows = select_attribute_rows(rows, None, top_attributes_per_event)
            attributes = [
                {
                    "table": str(getattr(a, "source_table", "")).upper(),
                    "column": str(getattr(a, "source_column", "")).upper(),
                }
                for a in attr_rows
            ]
            classifications = [str(getattr(x, "dbt_classification", "")) for x in rows]
            tables_dbg = {str(getattr(x, "source_table", "")).upper() for x in rows}
            out.append(
                EventLogCandidate(
                    activity=activity,
                    event_status="INVALID_EVENT",
                    event_time=None,
                    attributes=attributes,
                    source_tables=sorted(tables_dbg),
                    confidence="BAIXA",
                    dbt_alignment=aggregate_dbt_alignment(classifications),
                )
            )
            continue

        event_time = {
            "table": str(getattr(et_row, "source_table", "")).upper(),
            "column": str(getattr(et_row, "source_column", "")).upper(),
        }
        attributes = [
            {
                "table": str(getattr(a, "source_table", "")).upper(),
                "column": str(getattr(a, "source_column", "")).upper(),
            }
            for a in attr_rows
        ]
        tables: set[str] = {event_time["table"]}
        tables.update(a["table"] for a in attributes)

        cls_list = [str(getattr(et_row, "dbt_classification", ""))]
        cls_list.extend(str(getattr(a, "dbt_classification", "")) for a in attr_rows)

        conf = compute_event_confidence(
            float(getattr(et_row, "heuristic_score", 0.0)),
            str(getattr(et_row, "dbt_classification", "")),
        )
        dbt_agg = aggregate_dbt_alignment(cls_list)

        out.append(
            EventLogCandidate(
                activity=activity,
                event_status="OK",
                event_time=event_time,
                attributes=attributes,
                source_tables=sorted(tables),
                confidence=conf,
                dbt_alignment=dbt_agg,
            )
        )

    return out


def event_log_to_jsonable(records: list[EventLogCandidate]) -> list[dict[str, Any]]:
    """Serialização estável para JSON."""
    return [asdict(r) for r in records]
