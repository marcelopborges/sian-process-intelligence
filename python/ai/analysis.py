"""
Análise assistida por IA sobre resultados de mining/simulação.

Consome artefatos (variantes, gargalos, sumários) e produz texto interpretativo
ou estruturado. Não substitui métricas; apenas interpreta e comunica (ADR-006).
"""
from __future__ import annotations

from typing import Any


def interpret_variants(variant_results: "Any", context: str | None = None) -> str:
    """
    Gera interpretação em linguagem natural das variantes de processo.

    Args:
        variant_results: Saída de mining/variants (variantes, contagens).
        context: Texto opcional de contexto (ex.: processo Contas a Pagar).

    Returns:
        Texto explicativo para humanos. Não deve inventar números; basear em variant_results.

    TODO:
        - Integrar com LLM (prompt + variant_results).
        - Usar prompt de prompts/prompt_bottleneck_analysis.md ou similar.
        - Guardrail: não inventar métricas; citar origem.
    """
    raise NotImplementedError("Variant interpretation a implementar (LLM).")


def interpret_bottlenecks(bottleneck_results: "Any", context: str | None = None) -> str:
    """
    Gera interpretação dos gargalos identificados.

    Returns:
        Texto explicativo. Baseado apenas em bottleneck_results.
    """
    raise NotImplementedError("Bottleneck interpretation a implementar (LLM).")
