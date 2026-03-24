-- =============================================================================
-- Macro: cp_event_order — Ordem lógica para desempate de eventos no mesmo dia.
-- =============================================================================
-- Valores esperados (event log Contas a Pagar):
--   TITULO_CRIADO = 1, TITULO_LIBERADO = 2, EVENTO_FINANCEIRO_GERADO = 3,
--   LANCAMENTO_CONTABIL = 4, PAGAMENTO_REALIZADO = 5, BAIXA_SEM_SE5 = 5, TITULO_CANCELADO = 7.
-- Uso: na construção do event_timestamp_adjusted (offset por ordem).
-- =============================================================================

{% macro cp_event_order(activity_column) %}
case {{ activity_column }}
    when 'TITULO_CRIADO' then 1
    when 'TITULO_LIBERADO' then 2
    when 'EVENTO_FINANCEIRO_GERADO' then 3
    when 'LANCAMENTO_CONTABIL' then 4
    when 'PAGAMENTO_REALIZADO' then 5
    when 'BAIXA_SEM_SE5' then 5
    when 'TITULO_CANCELADO' then 7
    else 99
end
{% endmacro %}
