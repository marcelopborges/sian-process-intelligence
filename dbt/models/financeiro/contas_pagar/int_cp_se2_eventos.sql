-- =============================================================================
-- int_cp_se2_eventos — Eventos derivados da SE2 (TITULO_CRIADO, TITULO_CANCELADO)
-- =============================================================================
-- TITULO_CRIADO: um por caso, timestamp = e2_emissao (NEGOCIO) ou e2_dbalteracao (TECNICO).
-- TITULO_CANCELADO: um por caso quando status indica cancelado (join com chave de 7 campos).
-- HYPOTHESIS: Nome do campo de status na SE2 (ex.: E2_STATUS) e valores (ex.: 'C' cancelado)
-- a validar com ambiente real.
-- =============================================================================

with base as (
    select
        case_id,
        e2_emissao,
        e2_dbalteracao,
        e2_status
    from {{ ref('int_cp_se2_base') }}
),

criado as (
    select
        case_id,
        'TITULO_CRIADO' as activity,
        coalesce(timestamp(e2_emissao, '00:00:00'), e2_dbalteracao) as event_timestamp_original,
        case when e2_emissao is not null then 'NEGOCIO' else 'TECNICO' end as timestamp_confiabilidade,
        cast(null as string) as resource
    from base
),

cancelado as (
    select
        case_id,
        'TITULO_CANCELADO' as activity,
        e2_dbalteracao as event_timestamp_original,
        'TECNICO' as timestamp_confiabilidade,
        cast(null as string) as resource
    from base
    where trim(upper(coalesce(cast(e2_status as string), ''))) in ('C', 'CANCELADO', 'CANC')
),

unioned as (
    select * from criado
    union all
    select * from cancelado
)

select * from unioned
