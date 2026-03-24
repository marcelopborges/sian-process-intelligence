"""
Geração de recomendações de melhoria de processo assistida por IA.

Entrada: resultados de mining (variantes, gargalos) e/ou simulação.
Saída: recomendações em texto (ou estruturadas). Sempre com base nos dados;
IA não inventa fatos (ADR-006).
"""
from __future__ import annotations

from typing import Any


def generate_recommendations(
    mining_results: "Any",
    simulation_results: "Any" | None = None,
    constraints: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Gera recomendações de melhoria com base em mining e, opcionalmente, simulação.

    Args:
        mining_results: Variantes, gargalos, métricas de desempenho.
        simulation_results: Resultados de cenários simulados (opcional).
        constraints: Restrições a mencionar (ex.: "não aumentar headcount").

    Returns:
        Lista de recomendações; cada item pode ter título, descrição, base_em, prioridade.
        Formato a estabilizar quando integrar LLM.

    TODO:
        - Montar contexto a partir de mining_results e simulation_results.
        - Chamar LLM com prompt de prompts/prompt_recommendations ou similar.
        - Parsear resposta para estrutura lista de recomendações.
        - Guardrail: recomendações devem referenciar dados (ex.: atividade X, tempo Y).
    """
    raise NotImplementedError("Recommendations generation a implementar (LLM).")
