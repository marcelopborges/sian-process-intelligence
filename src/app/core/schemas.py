"""
Esquemas e convenções do event log (Contas a Pagar e modelo universal).

Define nomes de colunas obrigatórias e recomendadas para event logs
consumidos por mining e simulação. Alinhado ao mart_cp_event_log:
case_id, activity, event_timestamp_original, event_order, event_timestamp_adjusted,
timestamp_confiabilidade. Ver ADR-003 e decisões de modelagem em docs/.
"""
from __future__ import annotations

# --- Colunas obrigatórias do event log (Contas a Pagar) ---
CASE_ID = "case_id"
ACTIVITY = "activity"
# Timestamp principal para ordenação e mining (desempate por event_order)
EVENT_TIMESTAMP_ADJUSTED = "event_timestamp_adjusted"
EVENT_TIMESTAMP_ORIGINAL = "event_timestamp_original"
EVENT_ORDER = "event_order"
TIMESTAMP_CONFIABILIDADE = "timestamp_confiabilidade"

# Alias para compatibilidade: mining pode usar "timestamp" como evento efetivo
TIMESTAMP = EVENT_TIMESTAMP_ADJUSTED

# --- Colunas recomendadas ---
ACTIVITY_INSTANCE_ID = "activity_instance_id"
RESOURCE = "resource"
DURATION = "duration"

# --- Atividades Contas a Pagar (accepted_values no dbt) ---
ACTIVITIES_CP = [
    "TITULO_CRIADO",
    "TITULO_LIBERADO",
    "EVENTO_FINANCEIRO_GERADO",
    "LANCAMENTO_CONTABIL",
    "PAGAMENTO_REALIZADO",
    "BAIXA_SEM_SE5",
    "TITULO_CANCELADO",
]

# --- Valores de timestamp_confiabilidade ---
CONFIABILIDADE_NEGOCIO = "NEGOCIO"
CONFIABILIDADE_TECNICO = "TECNICO"


def required_columns() -> list[str]:
    """Colunas obrigatórias do event log para Process Mining (Contas a Pagar)."""
    return [
        CASE_ID,
        ACTIVITY,
        EVENT_TIMESTAMP_ADJUSTED,
        EVENT_TIMESTAMP_ORIGINAL,
        EVENT_ORDER,
        TIMESTAMP_CONFIABILIDADE,
    ]


def recommended_columns() -> list[str]:
    """Colunas recomendadas (opcionais)."""
    return [ACTIVITY_INSTANCE_ID, RESOURCE, DURATION]


def mining_timestamp_column() -> str:
    """Coluna de timestamp a usar para ordenação e mining (event_timestamp_adjusted)."""
    return EVENT_TIMESTAMP_ADJUSTED
