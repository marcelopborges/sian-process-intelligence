-- =============================================================================
-- cp_event_log (DuckDB) — Event log Contas a Pagar, laboratório local
-- =============================================================================
-- Contrato: docs/contracts/contas_a_pagar_process_intelligence.md (v1)
-- Atividades: TITULO_CRIADO, TITULO_LIBERADO (e2_datalib), EVENTO_FINANCEIRO_GERADO,
-- LANCAMENTO_CONTABIL, PAGAMENTO_REALIZADO, BAIXA_SEM_SE5 (saldo zero + baixa, sem SE5).
-- TITULO_CANCELADO não implementado (e2_datacan/e2_usuacan vazios no ambiente).
-- event_order (1-7), event_timestamp_adjusted, timestamp_confiabilidade (NEGOCIO/TECNICO).
-- FK2 agregado por caso. BAIXA_SEM_SE5 = pagamento/baixa sem evidência bancária.
-- =============================================================================

WITH se2_base AS (
    SELECT
        COALESCE(TRIM(CAST(e2_filial AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_prefixo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_num AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_parcela AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_tipo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_fornece AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e2_loja AS VARCHAR)), '') AS case_id,
        e2_emissao,
        "DBALTERACAO" AS e2_dbalteracao,
        e2_datalib,
        e2_saldo,
        e2_baixa
    FROM stg_se2
),
se5_case_ids AS (
    SELECT
        COALESCE(TRIM(CAST(e5_filial AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_prefixo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_numero AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_parcela AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_tipo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_clifor AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_loja AS VARCHAR)), '') AS case_id
    FROM stg_se5
    GROUP BY 1
),
eventos_se2 AS (
    SELECT case_id, 'TITULO_CRIADO' AS activity,
           COALESCE(CAST(e2_emissao AS TIMESTAMP), CAST(e2_dbalteracao AS TIMESTAMP)) AS event_timestamp_original,
           CASE WHEN e2_emissao IS NOT NULL THEN 'NEGOCIO' ELSE 'TECNICO' END AS timestamp_confiabilidade,
           CAST(NULL AS VARCHAR) AS resource
    FROM se2_base
    UNION ALL
    SELECT case_id, 'TITULO_LIBERADO',
           CAST(e2_datalib AS TIMESTAMP),
           'NEGOCIO',
           CAST(NULL AS VARCHAR)
    FROM se2_base
    WHERE e2_datalib IS NOT NULL
),
-- TITULO_CANCELADO não implementado: e2_datacan/e2_usuacan vazios no ambiente validado.
eventos_fk7 AS (
    SELECT
        COALESCE(TRIM(CAST("FK7_FILIAL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PREFIX" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_NUM" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PARCEL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_TIPO" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_CLIFOR" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_LOJA" AS VARCHAR)), '') AS case_id,
        'EVENTO_FINANCEIRO_GERADO' AS activity,
        CAST("DBALTERACAO" AS TIMESTAMP) AS event_timestamp_original,
        'TECNICO' AS timestamp_confiabilidade,
        CAST(NULL AS VARCHAR) AS resource
    FROM stg_fk7
),
fk7_case_id AS (
    SELECT
        "FK7_IDDOC",
        COALESCE(TRIM(CAST("FK7_FILIAL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PREFIX" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_NUM" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_PARCEL" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_TIPO" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_CLIFOR" AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST("FK7_LOJA" AS VARCHAR)), '') AS case_id
    FROM stg_fk7
),
eventos_fk2 AS (
    SELECT
        fk7_case_id.case_id,
        'LANCAMENTO_CONTABIL' AS activity,
        MIN(CAST("FK2_DATA" AS TIMESTAMP)) AS event_timestamp_original,
        'NEGOCIO' AS timestamp_confiabilidade,
        CAST(NULL AS VARCHAR) AS resource
    FROM stg_fk2
    JOIN fk7_case_id ON stg_fk2."FK2_IDDOC" = fk7_case_id."FK7_IDDOC"
    GROUP BY fk7_case_id.case_id
),
eventos_se5 AS (
    SELECT
        COALESCE(TRIM(CAST(e5_filial AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_prefixo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_numero AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_parcela AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_tipo AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_clifor AS VARCHAR)), '') || '|' ||
        COALESCE(TRIM(CAST(e5_loja AS VARCHAR)), '') AS case_id,
        'PAGAMENTO_REALIZADO' AS activity,
        MIN(CAST(strptime(CAST(e5_data AS VARCHAR), '%Y%m%d') AS TIMESTAMP)) AS event_timestamp_original,
        'NEGOCIO' AS timestamp_confiabilidade,
        CAST(NULL AS VARCHAR) AS resource
    FROM stg_se5
    GROUP BY 1
),
eventos_baixa_sem_se5 AS (
    SELECT
        se2_base.case_id,
        'BAIXA_SEM_SE5' AS activity,
        CAST(se2_base.e2_baixa AS TIMESTAMP) AS event_timestamp_original,
        'NEGOCIO' AS timestamp_confiabilidade,
        CAST(NULL AS VARCHAR) AS resource
    FROM se2_base
    LEFT JOIN se5_case_ids se5 ON se2_base.case_id = se5.case_id
    WHERE COALESCE(se2_base.e2_saldo, -1) = 0
      AND se2_base.e2_baixa IS NOT NULL
      AND se5.case_id IS NULL
),
unioned AS (
    SELECT case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource FROM eventos_se2
    UNION ALL SELECT case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource FROM eventos_fk7
    UNION ALL SELECT case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource FROM eventos_fk2
    UNION ALL SELECT case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource FROM eventos_se5
    UNION ALL SELECT case_id, activity, event_timestamp_original, timestamp_confiabilidade, resource FROM eventos_baixa_sem_se5
),
with_order AS (
    SELECT
        case_id,
        activity,
        event_timestamp_original,
        CASE activity
            WHEN 'TITULO_CRIADO' THEN 1
            WHEN 'TITULO_LIBERADO' THEN 2
            WHEN 'EVENTO_FINANCEIRO_GERADO' THEN 3
            WHEN 'LANCAMENTO_CONTABIL' THEN 4
            WHEN 'PAGAMENTO_REALIZADO' THEN 5
            WHEN 'BAIXA_SEM_SE5' THEN 5
            WHEN 'TITULO_CANCELADO' THEN 7
            ELSE 99
        END AS event_order,
        timestamp_confiabilidade,
        resource,
        COALESCE(event_timestamp_original, CAST('1900-01-01 00:00:00' AS TIMESTAMP))
            + (CASE activity WHEN 'TITULO_CRIADO' THEN 1 WHEN 'TITULO_LIBERADO' THEN 2 WHEN 'EVENTO_FINANCEIRO_GERADO' THEN 3
                WHEN 'LANCAMENTO_CONTABIL' THEN 4 WHEN 'PAGAMENTO_REALIZADO' THEN 5 WHEN 'BAIXA_SEM_SE5' THEN 5 WHEN 'TITULO_CANCELADO' THEN 7 ELSE 0 END) * 10 * INTERVAL 1 SECOND AS event_timestamp_adjusted
    FROM unioned
)
SELECT case_id, activity, event_timestamp_original, event_order, event_timestamp_adjusted, timestamp_confiabilidade, resource
FROM with_order
ORDER BY case_id, event_timestamp_adjusted, event_order;
