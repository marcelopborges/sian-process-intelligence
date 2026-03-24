-- =============================================================================
-- mart_cp_event_log — Event log de Contas a Pagar (Process Mining)
-- =============================================================================
-- Contrato: docs/contracts/contas_a_pagar_process_intelligence.md (v1)
-- case_id = chave de 7 campos (E2_*) com TRIM (origem no int).
-- Materialização: TABLE. Histórico estável e reprodutível.
-- Atividades: TITULO_CRIADO, TITULO_LIBERADO, EVENTO_FINANCEIRO_GERADO,
-- LANCAMENTO_CONTABIL, PAGAMENTO_REALIZADO, BAIXA_SEM_SE5, TITULO_CANCELADO.
-- timestamp_confiabilidade: NEGOCIO (data de negócio) ou TECNICO (ex.: DBALTERACAO).
-- Ordenação: event_order (1-7); event_timestamp_adjusted para desempate.
-- =============================================================================

{{ config(materialized='table') }}

with eventos_se2 as (
    select case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource
    from {{ ref('int_cp_se2_eventos') }}
),

eventos_fk7 as (
    select case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource
    from {{ ref('int_cp_fk7_eventos') }}
    where activity != 'EVENTO_FK7'
),

eventos_fk2 as (
    select case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource
    from {{ ref('int_cp_fk2_lancamentos') }}
),

eventos_se5 as (
    select case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource
    from {{ ref('int_cp_se5_pagamentos') }}
),

unioned as (
    select * from eventos_se2
    union all
    select * from eventos_fk7
    union all
    select * from eventos_fk2
    union all
    select * from eventos_se5
),

with_order as (
    select
        case_id,
        activity,
        event_timestamp_original,
        {{ cp_event_order('activity') }} as event_order,
        timestamp_confiabilidade,
        resource,
        timestamp_add(
            coalesce(event_timestamp_original, timestamp('1900-01-01 00:00:00')),
            interval ({{ cp_event_order('activity') }} * 10) second
        ) as event_timestamp_adjusted
    from unioned
),

ordered as (
    select
        case_id,
        activity,
        event_timestamp_original,
        event_order,
        event_timestamp_adjusted,
        timestamp_confiabilidade,
        resource
    from with_order
    order by case_id, event_timestamp_adjusted, event_order
)

select * from ordered
