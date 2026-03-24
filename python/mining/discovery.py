"""
Descoberta de modelo de processo a partir do event log.

Utiliza PM4Py (inductive miner, heuristic miner, etc.) para gerar
modelo (Petri net, BPMN ou DFG). Ver ADR-004.
"""
from __future__ import annotations

from typing import Any

# TODO: import pm4py e pandas quando implementar
# import pandas as pd
# from pm4py.algo.discovery import inductive, heuristic, dfg


def discover_process_model(
    event_log: "Any",
    algorithm: str = "inductive",
    **options: Any,
) -> Any:
    """
    Descobre um modelo de processo a partir do event log.

    Args:
        event_log: DataFrame com case_id, activity, timestamp (formato PM4Py).
        algorithm: 'inductive' | 'heuristic' | 'dfg' (ou outro suportado).
        **options: Parâmetros do algoritmo (ex.: noise_threshold para heuristic).

    Returns:
        Modelo (Petri net, BPMN ou DFG conforme algoritmo).
        Formato depende do PM4Py; documentar tipo de retorno quando implementar.

    TODO:
        - Converter DataFrame para formato PM4Py (pm4py.convert_to_event_log).
        - Chamar algoritmo escolhido e retornar modelo.
        - Export para arquivo (PNML, BPMN) opcional.
    """
    raise NotImplementedError("Discovery a implementar com PM4Py.")


def discover_dfg(event_log: "Any") -> Any:
    """
    Gera Directly-Follows Graph (DFG) a partir do event log.

    Útil para visualização rápida de fluxo sem modelo formal.
    """
    raise NotImplementedError("DFG discovery a implementar.")
