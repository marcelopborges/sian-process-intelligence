-- =============================================================================
-- mart_cp_ap_operacional — Camada operacional/dinâmica (aging, vencidos, SLA)
-- =============================================================================
-- Materialização: VIEW. Aqui podem existir cálculos com CURRENT_DATE().
-- Finalidade: dashboard operacional, aging, vencidos, SLA.
-- Não usar esta camada como fonte para Process Mining (usar case base e event log).
-- =============================================================================

{{ config(materialized='view') }}

with base as (
    select * from {{ ref('mart_cp_case_base') }}
),

with_operacional as (
    select
        *,
        date_diff(current_date(), data_vencimento, day) as dias_ate_vencimento,
        case
            when status_macro = 'PAGO' or status_macro = 'CANCELADO' then null
            when current_date() > data_vencimento then date_diff(current_date(), data_vencimento, day)
            else 0
        end as dias_vencido,
        case
            when status_macro = 'PAGO' or status_macro = 'CANCELADO' then 'encerrado'
            when current_date() > data_vencimento then 'vencido'
            else 'a_vencer'
        end as situacao_operacional
    from base
)

select * from with_operacional
