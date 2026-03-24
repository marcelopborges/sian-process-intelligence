-- =============================================================================
-- Macro: cp_case_id — Gera case_id a partir da chave composta de 7 campos (SE2).
-- =============================================================================
-- Decisão de modelagem: 1 caso = 1 título financeiro SE2.
-- Chave: E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA, E2_TIPO, E2_FORNECE, E2_LOJA.
-- TRIM nos componentes textuais para evitar colisão por espaços do Protheus.
-- Uso: {{ cp_case_id('e2_filial', 'e2_prefixo', 'e2_num', 'e2_parcela', 'e2_tipo', 'e2_fornece', 'e2_loja') }}
-- =============================================================================

{% macro cp_case_id(filial, prefixo, num, parcela, tipo, fornece, loja) %}
concat(
    coalesce(trim(cast({{ filial }} as string)), ''),
    '|',
    coalesce(trim(cast({{ prefixo }} as string)), ''),
    '|',
    coalesce(trim(cast({{ num }} as string)), ''),
    '|',
    coalesce(trim(cast({{ parcela }} as string)), ''),
    '|',
    coalesce(trim(cast({{ tipo }} as string)), ''),
    '|',
    coalesce(trim(cast({{ fornece }} as string)), ''),
    '|',
    coalesce(trim(cast({{ loja }} as string)), '')
)
{% endmacro %}
