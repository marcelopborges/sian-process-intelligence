"""
Análise de gargalos (bottlenecks) no processo.

Identifica atividades ou recursos com maior tempo de espera ou maior impacto
no tempo de ciclo. Base para recomendações de melhoria.
"""
from __future__ import annotations

from typing import Any


def compute_bottlenecks(
    event_log: "Any",
    level: str = "activity",
    **options: Any,
) -> "Any":
    """
    Calcula métricas de gargalo por atividade (ou por recurso).

    Args:
        event_log: DataFrame com case_id, activity, timestamp (e resource se level=resource).
        level: 'activity' | 'resource'.
        **options: Ex.: métricas (waiting_time, processing_time).

    Returns:
        DataFrame com atividade (ou recurso), tempo médio de espera, tempo de processamento,
        quantidade de casos, etc.

    TODO:
        - Usar PM4Py para performance (waiting/processing) ou calcular com pandas.
        - Ordenar por impacto (ex.: waiting time total) e retornar top N.
    """
    raise NotImplementedError("Bottleneck analysis a implementar.")


def bottleneck_summary(event_log: "Any", top_n: int = 10) -> dict[str, Any]:
    """
    Sumário executivo de gargalos: top N atividades e métricas principais.

    Formato adequado para consumo pela camada de IA (prompt de interpretação).
    """
    raise NotImplementedError("Bottleneck summary a implementar.")
