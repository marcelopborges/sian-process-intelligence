-- =============================================================================
-- stg_se5 — Staging da tabela SE5 (pagamentos)
-- =============================================================================
-- SE5 = melhor evidência bancária quando existir. Join com SE2 pela chave de 7 campos.
-- No Protheus pode ter E5_FILIAL, E5_NUM... HYPOTHESIS: Ajustar ao apontar para fonte real.
-- =============================================================================

select
    cast(null as string)   as e5_filial,
    cast(null as string)   as e5_prefixo,
    cast(null as string)   as e5_num,
    cast(null as string)   as e5_parcela,
    cast(null as string)   as e5_tipo,
    cast(null as string)   as e5_fornece,
    cast(null as string)   as e5_loja,
    cast(null as date)     as e5_data_pagamento,
    cast(null as string)   as e5_hora_pagamento,
    cast(null as float64)  as e5_valor_pago,
    cast(null as string)   as e5_usuario
from (select 1) x
where 1 = 0
