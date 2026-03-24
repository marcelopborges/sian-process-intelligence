-- =============================================================================
-- stg_se2 — Staging da tabela SE2 (títulos a pagar)
-- =============================================================================
-- Case ID = chave composta de 7 campos (E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA,
-- E2_TIPO, E2_FORNECE, E2_LOJA). TRIM nos textuais. Ver docs/domain-contas-a-pagar.md.
--
-- HYPOTHESIS: Nomes reais no Protheus podem ser E2_FILIAL, E2_PREFIXO, etc.
-- Ajustar alias ao apontar para a fonte real (ex.: from raw.se2).
-- =============================================================================

select
    cast(null as string)   as e2_filial,
    cast(null as string)   as e2_prefixo,
    cast(null as string)   as e2_num,
    cast(null as string)   as e2_parcela,
    cast(null as string)   as e2_tipo,
    cast(null as string)   as e2_fornece,
    cast(null as string)   as e2_loja,
    cast(null as float64)  as e2_valor,
    cast(null as string)   as e2_moeda,
    cast(null as date)     as e2_emissao,
    cast(null as date)     as e2_vencimento,
    cast(null as string)   as e2_status,
    cast(null as timestamp) as e2_dbalteracao
from (select 1) x
where 1 = 0
-- Substituir por: select E2_FILIAL as e2_filial, E2_PREFIXO as e2_prefixo, ... from {{ source('raw_protheus', 'se2') }}
