-- =============================================================================
-- cp_case_base (DuckDB) — Case base Contas a Pagar, laboratório local
-- =============================================================================
-- Contrato: docs/contracts/contas_a_pagar_process_intelligence.md (v1)
-- 1 caso = 1 título financeiro SE2. case_id = 7 campos com TRIM.
-- Status baseado em evidência validada: SE2 (saldo + baixa) = verdade operacional;
-- SE5 = evidência bancária. e2_status NÃO usado (inútil neste ambiente).
-- PAGO_SEM_SE5 = saldo zero + baixa preenchida + sem SE5. Cancelamento não implementado.
-- =============================================================================

WITH se2 AS (
    SELECT
        COALESCE(TRIM(CAST(e2_filial AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_prefixo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_num AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_parcela AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_tipo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_fornece AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_loja AS VARCHAR)), '') AS case_id,
        e2_filial AS filial,
        e2_fornece AS cod_fornecedor,
        e2_valor AS vl_titulo,
        e2_moeda AS moeda,
        e2_emissao AS data_emissao,
        e2_vencto AS data_vencimento,
        e2_status AS status_origem,
        e2_saldo,
        e2_baixa
    FROM stg_se2
),
se5_keys AS (
    SELECT
        COALESCE(TRIM(CAST(e5_filial AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_prefixo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_numero AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_parcela AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_tipo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_clifor AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_loja AS VARCHAR)), '') AS case_id,
        MIN(CAST(strptime(CAST(e5_data AS VARCHAR), '%Y%m%d') AS DATE)) AS dt_pagamento_banco,
        SUM(e5_valor) AS vl_pago_observado
    FROM stg_se5
    GROUP BY 1
),
fk7_tem AS (
    SELECT
        COALESCE(TRIM(CAST("FK7_FILIAL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PREFIX" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_NUM" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PARCEL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_TIPO" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_CLIFOR" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_LOJA" AS VARCHAR)), '') AS case_id
    FROM stg_fk7
    GROUP BY 1
),
final AS (
    SELECT
        se2.case_id,
        se2.filial,
        se2.cod_fornecedor,
        se2.vl_titulo,
        se2.moeda,
        se2.data_emissao,
        se2.data_vencimento,
        se2.status_origem,
        CASE
            WHEN se5.case_id IS NOT NULL THEN 'PAGO'
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN 'PAGO_SEM_SE5'
            WHEN fk7.case_id IS NOT NULL THEN 'EM_PROCESSAMENTO'
            ELSE 'ABERTO'
        END AS status_macro,
        CASE
            WHEN se5.case_id IS NOT NULL THEN 'PAGO_COM_SE5'
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN 'PAGO_SEM_SE5'
            WHEN fk7.case_id IS NOT NULL THEN 'EM_PROCESSAMENTO'
            ELSE 'ABERTO'
        END AS status_detalhado,
        (fk7.case_id IS NOT NULL) AS tem_fk7,
        (se5.case_id IS NOT NULL) AS tem_se5,
        se5.dt_pagamento_banco AS fonte_dt_pagamento,
        se5.vl_pago_observado AS vl_pago_observado,
        CASE
            WHEN se5.case_id IS NOT NULL THEN se5.vl_pago_observado
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN se2.vl_titulo
            ELSE NULL
        END AS vl_pago_consolidado,
        CASE
            WHEN se5.case_id IS NOT NULL THEN FALSE
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN TRUE
            ELSE FALSE
        END AS vl_pago_e_inferido,
        se2.data_emissao AS data_inicio_processo,
        CASE
            WHEN se5.case_id IS NOT NULL THEN se5.dt_pagamento_banco
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN CAST(se2.e2_baixa AS DATE)
            ELSE NULL
        END AS data_fim_processo,
        CASE
            WHEN se5.case_id IS NOT NULL THEN DATEDIFF('day', se2.data_emissao, se5.dt_pagamento_banco)
            WHEN COALESCE(se2.e2_saldo, -1) = 0 AND se2.e2_baixa IS NOT NULL AND se5.case_id IS NULL THEN DATEDIFF('day', se2.data_emissao, CAST(se2.e2_baixa AS DATE))
            ELSE NULL
        END AS duracao_dias
    FROM se2
    LEFT JOIN se5_keys se5 ON se2.case_id = se5.case_id
    LEFT JOIN fk7_tem fk7 ON se2.case_id = fk7.case_id
)
SELECT * FROM final;
