-- =============================================================================
-- stg_fk2 — Staging da tabela FK2 (lançamentos contábeis)
-- =============================================================================
-- Join com SE2 pela chave de 7 campos. No Protheus pode ter F2_FILIAL, F2_NUM...
-- No event log principal: LANCAMENTO_CONTABIL agregado por caso (não um evento por rateio).
-- HYPOTHESIS: Ajustar nomes ao apontar para fonte real.
-- =============================================================================

select
    cast(null as string)   as f2_filial,
    cast(null as string)   as f2_prefixo,
    cast(null as string)   as f2_num,
    cast(null as string)   as f2_parcela,
    cast(null as string)   as f2_tipo,
    cast(null as string)   as f2_fornece,
    cast(null as string)   as f2_loja,
    cast(null as date)     as f2_data_lancamento,
    cast(null as string)   as f2_hora_lancamento,
    cast(null as string)   as f2_tipo_lancamento,
    cast(null as string)   as f2_usuario,
    cast(null as timestamp) as f2_dbalteracao
from (select 1) x
where 1 = 0
