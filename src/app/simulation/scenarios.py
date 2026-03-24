"""
Simulação de cenários de processo com SimPy.

Modelo discreto por eventos: atividades, recursos (ex.: analistas), filas.
Parâmetros podem ser estimados a partir do event log (mining) ou definidos manualmente.
"""
from __future__ import annotations

from typing import Any


def run_simulation(
    scenario: dict[str, Any],
    replications: int = 10,
    **sim_options: Any,
) -> Any:
    """
    Executa N replicações do cenário de simulação e agrega resultados.

    Args:
        scenario: Definição do cenário (atividades, recursos, tempos, regras).
                  Estrutura a definir (ex.: número de recursos por tipo, distribuições).
        replications: Número de replicações para obter métricas estáveis.
        **sim_options: Ex.: tempo máximo de simulação, seed.

    Returns:
        Resultados agregados: tempo de ciclo médio, utilização de recursos,
        throughput, etc. (DataFrame ou dict).

    TODO:
        - Implementar modelo SimPy a partir de 'scenario'.
        - Rodar replications vezes e coletar métricas.
        - Retornar estrutura padronizada para relatório e IA.
    """
    raise NotImplementedError("Simulation runner a implementar com SimPy.")


def build_scenario_from_event_log(event_log: Any) -> dict[str, Any]:
    """
    Gera parâmetros de cenário (tempos médios, recursos) a partir do event log.

    Útil para calibrar simulação com dados reais. Não substitui validação de negócio.
    """
    raise NotImplementedError("Scenario builder from event log a implementar.")
