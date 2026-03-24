-- =============================================================================
-- mart_cp_case_base — Case base de Contas a Pagar (estático, reprodutível)
-- =============================================================================
-- Contrato: docs/contracts/contas_a_pagar_process_intelligence.md (v1)
-- 1 caso = 1 título financeiro SE2. case_id = chave de 7 campos (E2_*) com TRIM (int).
-- Materialização: TABLE. Status estático (sem uso de data atual em status_macro/status_detalhado).
-- Valor observado (SE2, SE5) vs inferido; flag vl_pago_e_inferido explícita.
-- =============================================================================

{{ config(materialized='table') }}

with se2 as (
    select * from {{ ref('int_cp_se2_base') }}
),

se5_agg as (
    select case_id, dt_pagamento_banco, vl_pago_observado
    from {{ ref('int_cp_se5_resumo') }}
),

fk7_tem as (
    select case_id, 1 as tem_fk7
    from {{ ref('int_cp_fk7_eventos') }}
    group by case_id
),

final as (
    select
        se2.case_id,
        se2.e2_filial as filial,
        se2.e2_fornece as cod_fornecedor,
        se2.e2_valor as vl_titulo,
        se2.e2_moeda as moeda,
        se2.e2_emissao as data_emissao,
        se2.e2_vencimento as data_vencimento,
        se2.e2_status as status_origem,
        case
            when trim(upper(coalesce(cast(se2.e2_status as string), ''))) in ('C', 'CANCELADO', 'CANC') then 'CANCELADO'
            when se5.dt_pagamento_banco is not null or se5.vl_pago_observado is not null then 'PAGO'
            when fk7.tem_fk7 = 1 then 'EM_ANDAMENTO'
            else 'ABERTO'
        end as status_macro,
        coalesce(cast(se2.e2_status as string), '') as status_detalhado,
        case when fk7.case_id is not null then true else false end as tem_fk7,
        case when se5.case_id is not null then true else false end as tem_se5,
        se5.dt_pagamento_banco as fonte_dt_pagamento,
        se5.vl_pago_observado as vl_pago_observado,
        coalesce(se5.vl_pago_observado, case when se2.e2_status in ('B', 'PAGO', 'P') then se2.e2_valor else null end) as vl_pago_consolidado,
        case when se5.case_id is null and se2.e2_status in ('B', 'PAGO', 'P') then true else false end as vl_pago_e_inferido,
        se2.e2_emissao as data_inicio_processo,
        coalesce(se5.dt_pagamento_banco, se2.e2_vencimento) as data_fim_processo,
        date_diff(coalesce(se5.dt_pagamento_banco, se2.e2_vencimento), se2.e2_emissao, day) as duracao_dias
    from se2
    left join se5_agg se5 on se2.case_id = se5.case_id
    left join fk7_tem fk7 on se2.case_id = fk7.case_id
)

select * from final
