"""
Análise de variantes de processo.

Identifica traços (sequências de atividades por caso) e agrupa em variantes,
com contagem e percentual. Base para interpretação de desvio e padrões.
"""
from __future__ import annotations

from typing import Any


def get_variants(event_log: "Any", max_variants: int | None = 50) -> "Any":
    """
    Extrai variantes (traços únicos) com contagem de casos.

    Args:
        event_log: DataFrame com case_id, activity, timestamp.
        max_variants: Limite de variantes a retornar (evitar explosão).

    Returns:
        DataFrame ou estrutura com: variante (traço), count, percentual.
        Formato a definir (ex.: list of dict ou DataFrame).

    TODO:
        - Ordenar eventos por caso e timestamp.
        - Agrupar por sequência de atividades (traço).
        - Contar e ordenar por frequência.
    """
    raise NotImplementedError("Variants analysis a implementar (PM4Py ou pandas).")


def variant_summary(event_log: "Any") -> dict[str, Any]:
    """
    Sumário de variantes: total de casos, total de variantes, top N.

    Útil para alimentar camada de IA (interpretação) e relatórios.
    """
    raise NotImplementedError("Variant summary a implementar.")
