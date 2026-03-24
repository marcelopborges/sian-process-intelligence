# Arquitetura — SIAN Process Intelligence

## Visão de alto nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Fontes (Protheus) → BigQuery (raw/staging)                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  dbt: staging → int → mart                                               │
│  Três saídas distintas:                                                  │
│  • mart_cp_case_base (TABLE, estático)                                   │
│  • mart_cp_event_log (TABLE, Process Mining, ordenação estável)          │
│  • mart_cp_ap_operacional (VIEW, dinâmica, aging/SLA)                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Python: connectors → core (schemas) → mining / simulation / ai         │
│  Event log: case_id, activity, event_timestamp_adjusted,                 │
│  timestamp_confiabilidade, event_order                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Separação arquitetural (Contas a Pagar)

1. **mart_cp_case_base** (TABLE)
   - Estático e reprodutível; sem CURRENT_DATE() em status principal.
   - 1 caso = 1 título SE2; case_id = chave de 7 campos (E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA, E2_TIPO, E2_FORNECE, E2_LOJA) com TRIM.
   - status_macro, status_detalhado, tem_fk7, tem_se5, fonte_dt_pagamento, vl_pago_consolidado, vl_pago_e_inferido.

2. **mart_cp_event_log** (TABLE)
   - Focado em Process Mining; histórico estável.
   - event_timestamp_original, event_order, event_timestamp_adjusted, timestamp_confiabilidade (NEGOCIO/TECNICO).
   - Atividades: TITULO_CRIADO, TITULO_LIBERADO, EVENTO_FINANCEIRO_GERADO, LANCAMENTO_CONTABIL, PAGAMENTO_REALIZADO, BAIXA_SEM_SE5, TITULO_CANCELADO.
   - FK2 agregado por caso; BAIXA_MANUAL renomeado para BAIXA_SEM_SE5.

3. **mart_cp_ap_operacional** (VIEW)
   - Camada operacional/dinâmica; pode usar CURRENT_DATE() para aging, vencidos, SLA.
   - Não usar como fonte para Process Mining.

## Camadas de dados (dbt)

- **Staging**: 7 campos da chave + demais colunas por tabela (SE2, FK7, FK2, SE5). Nomes reais a validar no ambiente (HYPOTHESIS nos stubs).
- **Int**: int_cp_se2_base (case_id via macro), int_cp_se2_eventos, int_cp_fk7_eventos, int_cp_fk2_lancamentos (agregado), int_cp_se5_pagamentos, int_cp_se5_resumo.
- **Mart**: case base, event log, ap_operacional conforme acima.

## Python

- **connectors**: leitura do event log (colunas alinhadas ao mart_cp_event_log, incluindo event_timestamp_adjusted e timestamp_confiabilidade).
- **core/schemas**: constantes para case_id, activity, event_timestamp_adjusted, event_order, timestamp_confiabilidade, lista de atividades CP.
- **mining**: usa event_timestamp_adjusted como timestamp efetivo para ordenação.

## Decisões de referência

- **Event log universal**: ADR-003 (com extensão: event_order, timestamp_confiabilidade, event_timestamp_adjusted).
- **Case base vs event log vs análise**: ADR-010.
- **Processo inicial e chave do caso**: docs/domain-contas-a-pagar.md e ADR-008.
- **DBALTERACAO**: tratado como TECNICO; não como verdade absoluta (docs/domain-contas-a-pagar.md).
