-- Teste: cada case_id deve ter exatamente 1 evento TITULO_CRIADO.
-- Falha se existir case_id com 0 ou mais de 1 TITULO_CRIADO.
select
    case_id,
    cnt as num_titulo_criado
from (
    select case_id, count(*) as cnt
    from {{ ref('mart_cp_event_log') }}
    where activity = 'TITULO_CRIADO'
    group by case_id
)
where cnt != 1
