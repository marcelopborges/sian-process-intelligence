-- =============================================================================
-- int_cp_se2_base — Base de títulos a pagar (SE2)
-- =============================================================================
-- Decisão: 1 caso = 1 título financeiro SE2.
-- Case ID = chave composta de 7 campos com TRIM (macro cp_case_id).
-- Saída: case_id + componentes da chave + valor, datas, status para case base e event log.
-- =============================================================================

with source as (
    select * from {{ ref('stg_se2') }}
),

base as (
    select
        {{ cp_case_id('e2_filial', 'e2_prefixo', 'e2_num', 'e2_parcela', 'e2_tipo', 'e2_fornece', 'e2_loja') }} as case_id,
        e2_filial,
        e2_prefixo,
        e2_num,
        e2_parcela,
        e2_tipo,
        e2_fornece,
        e2_loja,
        e2_valor,
        e2_moeda,
        e2_emissao,
        e2_vencimento,
        e2_status,
        e2_dbalteracao
    from source
)

select * from base
