-- =============================================================================
-- stg_fk7 — Staging da tabela FK7 (eventos/workflow)
-- =============================================================================
-- Join com SE2 pela chave de 7 campos. No Protheus a FK7 pode ter F7_FILIAL, F7_NUM...
-- HYPOTHESIS: Ajustar nomes ao apontar para fonte real; garantir 7 campos para join.
-- DBALTERACAO quando usado como proxy de tempo → timestamp_confiabilidade = TECNICO.
-- =============================================================================

select
    cast(null as string)   as f7_filial,
    cast(null as string)   as f7_prefixo,
    cast(null as string)   as f7_num,
    cast(null as string)   as f7_parcela,
    cast(null as string)   as f7_tipo,
    cast(null as string)   as f7_fornece,
    cast(null as string)   as f7_loja,
    cast(null as string)   as f7_cod_evento,
    cast(null as date)     as f7_data_evento,
    cast(null as string)   as f7_hora_evento,
    cast(null as string)   as f7_usuario,
    cast(null as timestamp) as f7_dbalteracao
from (select 1) x
where 1 = 0
