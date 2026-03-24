-- Teste: casos com status_macro = PAGO devem ter evento terminal PAGAMENTO_REALIZADO ou BAIXA_SEM_SE5.
-- Falha se existir caso PAGO sem nenhum desses eventos.
select
    c.case_id,
    c.status_macro
from {{ ref('mart_cp_case_base') }} c
left join (
    select distinct case_id
    from {{ ref('mart_cp_event_log') }}
    where activity in ('PAGAMENTO_REALIZADO', 'BAIXA_SEM_SE5')
) t on c.case_id = t.case_id
where c.status_macro = 'PAGO'
  and t.case_id is null
