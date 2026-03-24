-- =============================================================================
-- int_cp_fk7_eventos — Eventos da FK7 (workflow / evento financeiro)
-- =============================================================================
-- FK7 = elo do evento financeiro. Join com SE2 pela chave de 7 campos.
-- Mapeamento cod_evento → activity: TITULO_LIBERADO, EVENTO_FINANCEIRO_GERADO (e outros
-- conforme catálogo FK7). BAIXA_MANUAL renomeado para BAIXA_SEM_SE5 no mart.
-- timestamp_confiabilidade: NEGOCIO quando data de negócio; TECNICO quando DBALTERACAO.
-- HYPOTHESIS: Nomes exatos de cod_evento FK7 a validar com ambiente real.
-- =============================================================================

with se2_base as (
    select case_id, e2_filial, e2_prefixo, e2_num, e2_parcela, e2_tipo, e2_fornece, e2_loja from {{ ref('int_cp_se2_base') }}
),

source as (
    select
        se2.case_id,
        fk7.f7_cod_evento,
        fk7.f7_data_evento,
        fk7.f7_hora_evento,
        fk7.f7_usuario,
        fk7.f7_dbalteracao
    from {{ ref('stg_fk7') }} fk7
    inner join se2_base se2
        on  trim(cast(fk7.f7_filial as string))   = trim(cast(se2.e2_filial as string))
        and trim(cast(fk7.f7_prefixo as string))   = trim(cast(se2.e2_prefixo as string))
        and trim(cast(fk7.f7_num as string))       = trim(cast(se2.e2_num as string))
        and trim(cast(fk7.f7_parcela as string))   = trim(cast(se2.e2_parcela as string))
        and trim(cast(fk7.f7_tipo as string))      = trim(cast(se2.e2_tipo as string))
        and trim(cast(fk7.f7_fornece as string))  = trim(cast(se2.e2_fornece as string))
        and trim(cast(fk7.f7_loja as string))      = trim(cast(se2.e2_loja as string))
),

mapped as (
    select
        case_id,
        case
            when f7_cod_evento in ('LIBERADO', 'LIB') then 'TITULO_LIBERADO'
            when f7_cod_evento in ('EVTFIN', 'EVENTO_FIN') then 'EVENTO_FINANCEIRO_GERADO'
            when f7_cod_evento in ('BAIXA_MANUAL', 'BAIXA') then 'BAIXA_SEM_SE5'
            else coalesce(f7_cod_evento, 'EVENTO_FK7')
        end as activity,
        coalesce(
            timestamp(f7_data_evento, coalesce(f7_hora_evento, '00:00:00')),
            f7_dbalteracao
        ) as event_timestamp_original,
        case
            when f7_data_evento is not null then 'NEGOCIO'
            else 'TECNICO'
        end as timestamp_confiabilidade,
        f7_usuario as resource
    from source
)

select * from mapped
