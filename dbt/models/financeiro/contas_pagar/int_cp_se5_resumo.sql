-- =============================================================================
-- int_cp_se5_resumo — Resumo de pagamentos SE5 por caso (para case base)
-- =============================================================================
-- Agregação por case_id: dt_pagamento_banco (min), vl_pago_observado (sum).
-- Usado pelo mart_cp_case_base para valor observado e fonte_dt_pagamento.
-- =============================================================================

with se2_keys as (
    select case_id, e2_filial, e2_prefixo, e2_num, e2_parcela, e2_tipo, e2_fornece, e2_loja from {{ ref('int_cp_se2_base') }}
),

agg as (
    select
        se2.case_id,
        min(timestamp(se5.e5_data_pagamento, coalesce(se5.e5_hora_pagamento, '00:00:00'))) as dt_pagamento_banco,
        sum(se5.e5_valor_pago) as vl_pago_observado
    from {{ ref('stg_se5') }} se5
    inner join se2_keys se2
        on  trim(cast(se5.e5_filial as string))   = trim(cast(se2.e2_filial as string))
        and trim(cast(se5.e5_prefixo as string))  = trim(cast(se2.e2_prefixo as string))
        and trim(cast(se5.e5_num as string))      = trim(cast(se2.e2_num as string))
        and trim(cast(se5.e5_parcela as string))  = trim(cast(se2.e2_parcela as string))
        and trim(cast(se5.e5_tipo as string))     = trim(cast(se2.e2_tipo as string))
        and trim(cast(se5.e5_fornece as string)) = trim(cast(se2.e2_fornece as string))
        and trim(cast(se5.e5_loja as string))     = trim(cast(se2.e2_loja as string))
    group by se2.case_id
)

select * from agg
