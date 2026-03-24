-- =============================================================================
-- cp_event_log_semantic (DuckDB) — Event log semântico (interpretável)
-- =============================================================================
-- Fonte: cp_event_log (técnico) já materializado no DuckDB local.
--
-- Objetivo:
-- - Trilha canônica por caso: todo case_id ancorado em TITULO_CRIADO.
-- - Casos sem TITULO_CRIADO são excluídos (variantes inválidas).
-- - 1 linha = 1 etapa semântica por case_id (deduplicação por primeira ocorrência).
-- - Um único evento final por case: PAGAMENTO_REALIZADO, ou senão BAIXA_SEM_SE5.
--
-- Saída: case_id, activity, event_timestamp_original, event_timestamp_semantic,
--        event_order_semantic, timestamp_confiabilidade, source_table, resource
-- =============================================================================

WITH base AS (
    SELECT
        case_id,
        activity,
        event_timestamp_original,
        timestamp_confiabilidade,
        CAST(NULL AS VARCHAR) AS source_table,
        resource
    FROM cp_event_log
    WHERE activity IN (
        'TITULO_CRIADO',
        'EVENTO_FINANCEIRO_GERADO',
        'TITULO_LIBERADO',
        'LANCAMENTO_CONTABIL',
        'PAGAMENTO_REALIZADO',
        'BAIXA_SEM_SE5'
    )
),

-- Deduplicação: primeira ocorrência cronológica por (case_id, activity)
dedup AS (
    SELECT
        case_id,
        activity,
        MIN(event_timestamp_original) AS event_timestamp_original,
        arg_min(timestamp_confiabilidade, event_timestamp_original) AS timestamp_confiabilidade,
        arg_min(source_table, event_timestamp_original) AS source_table,
        arg_min(resource, event_timestamp_original) AS resource
    FROM base
    GROUP BY 1, 2
),

-- Ancoragem: só casos que têm TITULO_CRIADO (elimina variantes que começam em
-- EVENTO_FINANCEIRO_GERADO, PAGAMENTO_REALIZADO, etc.)
cases_with_titulo AS (
    SELECT DISTINCT case_id
    FROM dedup
    WHERE activity = 'TITULO_CRIADO'
),

anchored AS (
    SELECT d.*
    FROM dedup d
    INNER JOIN cases_with_titulo c ON d.case_id = c.case_id
),

flags AS (
    SELECT
        case_id,
        MAX(CASE WHEN activity = 'PAGAMENTO_REALIZADO' THEN 1 ELSE 0 END) AS has_pagamento,
        MAX(CASE WHEN activity = 'BAIXA_SEM_SE5' THEN 1 ELSE 0 END) AS has_baixa_sem_se5
    FROM anchored
    GROUP BY 1
),

-- Um único evento final: PAGAMENTO_REALIZADO prevalece; senão BAIXA_SEM_SE5
filtered_final AS (
    SELECT a.*
    FROM anchored a
    JOIN flags f ON a.case_id = f.case_id
    WHERE NOT (a.activity = 'BAIXA_SEM_SE5' AND f.has_pagamento = 1)
),

with_semantic_order AS (
    SELECT
        case_id,
        activity,
        event_timestamp_original,
        CASE activity
            WHEN 'TITULO_CRIADO' THEN 1
            WHEN 'EVENTO_FINANCEIRO_GERADO' THEN 2
            WHEN 'TITULO_LIBERADO' THEN 3
            WHEN 'LANCAMENTO_CONTABIL' THEN 4
            WHEN 'PAGAMENTO_REALIZADO' THEN 5
            WHEN 'BAIXA_SEM_SE5' THEN 5
            ELSE 99
        END AS event_order_semantic,
        timestamp_confiabilidade,
        source_table,
        resource,
        COALESCE(event_timestamp_original, CAST('1900-01-01 00:00:00' AS TIMESTAMP))
          + (CASE activity
                WHEN 'TITULO_CRIADO' THEN 1
                WHEN 'EVENTO_FINANCEIRO_GERADO' THEN 2
                WHEN 'TITULO_LIBERADO' THEN 3
                WHEN 'LANCAMENTO_CONTABIL' THEN 4
                WHEN 'PAGAMENTO_REALIZADO' THEN 5
                WHEN 'BAIXA_SEM_SE5' THEN 5
                ELSE 0
            END) * 10 * INTERVAL 1 SECOND AS event_timestamp_semantic
    FROM filtered_final
)

SELECT
    case_id,
    activity,
    event_timestamp_original,
    event_timestamp_semantic,
    event_order_semantic,
    timestamp_confiabilidade,
    source_table,
    resource
FROM with_semantic_order
ORDER BY case_id, event_timestamp_semantic, event_order_semantic;

