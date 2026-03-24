-- =============================================================================
-- int_cp_fk2_lancamentos — Lançamentos contábeis (FK2) agregados por caso
-- =============================================================================
-- Decisão: no event log principal, LANCAMENTO_CONTABIL = um evento por caso (agregado).
-- Não gerar um evento por rateio FK2 na V1. Valor no evento agregado: NULL (evitar ambiguidade).
-- timestamp_confiabilidade: NEGOCIO se data de lançamento; TECNICO se DBALTERACAO.
-- =============================================================================

with se2_keys as (
    select case_id, e2_filial, e2_prefixo, e2_num, e2_parcela, e2_tipo, e2_fornece, e2_loja from {{ ref('int_cp_se2_base') }}
),

fk2_agg as (
    select
        se2.case_id,
        min(timestamp(fk2.f2_data_lancamento, coalesce(fk2.f2_hora_lancamento, '00:00:00'))) as event_timestamp_original,
        min(fk2.f2_dbalteracao) as fallback_ts
    from {{ ref('stg_fk2') }} fk2
    inner join se2_keys se2
        on  trim(cast(fk2.f2_filial as string))   = trim(cast(se2.e2_filial as string))
        and trim(cast(fk2.f2_prefixo as string))  = trim(cast(se2.e2_prefixo as string))
        and trim(cast(fk2.f2_num as string))      = trim(cast(se2.e2_num as string))
        and trim(cast(fk2.f2_parcela as string))  = trim(cast(se2.e2_parcela as string))
        and trim(cast(fk2.f2_tipo as string))     = trim(cast(se2.e2_tipo as string))
        and trim(cast(fk2.f2_fornece as string))  = trim(cast(se2.e2_fornece as string))
        and trim(cast(fk2.f2_loja as string))     = trim(cast(se2.e2_loja as string))
    group by se2.case_id
),

mapped as (
    select
        case_id,
        'LANCAMENTO_CONTABIL' as activity,
        coalesce(event_timestamp_original, fallback_ts) as event_timestamp_original,
        case
            when event_timestamp_original is not null then 'NEGOCIO'
            else 'TECNICO'
        end as timestamp_confiabilidade,
        cast(null as string) as resource
    from fk2_agg
)

select * from mapped
