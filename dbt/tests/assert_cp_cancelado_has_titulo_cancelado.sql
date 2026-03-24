-- Teste: casos com status_macro = CANCELADO devem ter evento TITULO_CANCELADO.
-- Falha se existir caso CANCELADO sem TITULO_CANCELADO no event log.
select
    c.case_id,
    c.status_macro
from {{ ref('mart_cp_case_base') }} c
left join (
    select distinct case_id
    from {{ ref('mart_cp_event_log') }}
    where activity = 'TITULO_CANCELADO'
) t on c.case_id = t.case_id
where c.status_macro = 'CANCELADO'
  and t.case_id is null
