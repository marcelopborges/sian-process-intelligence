"""Validação leve de sequência de arestas (sanidade do fluxo linear)."""
from __future__ import annotations


def validate_linear_edges(edges: list[dict[str, str]]) -> list[str]:
    """Retorna avisos se a cadeia `from`→`to` não for contínua (fluxo linear esperado)."""
    if len(edges) < 2:
        return []
    issues: list[str] = []
    for i in range(len(edges) - 1):
        cur_to = str(edges[i].get("to", "") or "")
        nxt_from = str(edges[i + 1].get("from", "") or "")
        if cur_to != nxt_from:
            issues.append(
                f"quebra_cadeia[{i}]: to={cur_to!r} != próximo from={nxt_from!r}"
            )
    return issues
