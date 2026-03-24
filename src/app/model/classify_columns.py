"""
Classificação heurística do papel da coluna (nome físico Protheus / SX3).

Sem LLM. Usada antes da seleção de event_time e atributos no event log candidato.
"""
from __future__ import annotations

ColumnRole = str  # EVENT_TIME | ATTRIBUTE | IDENTIFIER | STATUS | UNKNOWN


def classify_column_role(column_name: str) -> ColumnRole:
    """
    Infere o papel pelo nome da coluna (maiúsculas).

    Ordem de precedência: EVENT_TIME → ATTRIBUTE → IDENTIFIER → STATUS → UNKNOWN.
    """
    c = (column_name or "").strip().upper()
    if not c:
        return "UNKNOWN"

    def contains_any(subs: tuple[str, ...]) -> bool:
        return any(s in c for s in subs)

    # EVENT_TIME — datas / horas / emissão / baixa / alteração técnica
    event_markers = (
        "DATA",
        "DT",
        "DATALIB",
        "EMISSAO",
        "BAIXA",
        "DBALTERACAO",
        "HORA",
        "LANCAM",
        "LANCTO",
        "PAGTO",
        "MOVIMENT",
        "VENCIMENTO",
        "EVENTO",
    )
    if contains_any(event_markers):
        return "EVENT_TIME"

    # ATTRIBUTE — valores e dimensões de negócio frequentes
    attr_markers = (
        "VALOR",
        "VALLIQ",
        "BANCO",
        "AGENCIA",
        "CONTA",
        "CCD",
        "CREDITO",
        "DEBITO",
    )
    if contains_any(attr_markers):
        return "ATTRIBUTE"

    # IDENTIFIER — chaves e sequências
    id_markers = ("PREFIXO", "SEQ", "NUM", "COD", "ID")
    if contains_any(id_markers):
        return "IDENTIFIER"

    # STATUS — estado do registro
    if "STATUS" in c:
        return "STATUS"
    if c == "OK" or c.endswith("_OK"):
        return "STATUS"

    return "UNKNOWN"
