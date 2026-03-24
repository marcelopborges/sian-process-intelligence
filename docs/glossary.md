# Glossário — SIAN Process Intelligence

Termos usados no projeto com definição operacional. Alinhado às decisões de modelagem de Contas a Pagar.

| Termo | Definição |
|-------|-----------|
| **Case** | Uma instância do processo. Em Contas a Pagar: **1 caso = 1 título financeiro SE2**. Identificado por `case_id`. |
| **case_id** | Chave composta de 7 campos com TRIM: E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA, E2_TIPO, E2_FORNECE, E2_LOJA (documentado no modelo e em docs/domain-contas-a-pagar.md). |
| **Case base** | mart_cp_case_base (TABLE). Estático e reprodutível; sem CURRENT_DATE() em status_macro/status_detalhado. status_macro, tem_fk7, tem_se5, vl_pago_consolidado, vl_pago_e_inferido. |
| **Event log** | mart_cp_event_log (TABLE). case_id, activity, event_timestamp_original, event_order, event_timestamp_adjusted, timestamp_confiabilidade. Fonte para Process Mining. |
| **event_timestamp_adjusted** | Timestamp derivado do original com offset por event_order; usado para ordenação estável no mining. |
| **timestamp_confiabilidade** | NEGOCIO (data de negócio forte) ou TECNICO (ex.: DBALTERACAO como proxy). Coluna explícita no event log. |
| **Activity** | Nome padronizado no event log: TITULO_CRIADO, TITULO_LIBERADO, EVENTO_FINANCEIRO_GERADO, LANCAMENTO_CONTABIL, PAGAMENTO_REALIZADO, BAIXA_SEM_SE5, TITULO_CANCELADO. |
| **BAIXA_SEM_SE5** | Nome padrão no log; qualquer BAIXA_MANUAL é renomeada para BAIXA_SEM_SE5. |
| **vl_pago_e_inferido** | Flag no case base: true quando o valor consolidado foi inferido (ex.: baixa sem SE5); não mascarar ausência de SE5 como fato bancário. |
| **status_macro** | Status estático no case base (ABERTO, EM_ANDAMENTO, PAGO, CANCELADO). Não depende de CURRENT_DATE(). |
| **mart_cp_ap_operacional** | VIEW operacional; pode usar CURRENT_DATE() para aging, vencidos, SLA. Não usar para Process Mining. |
| **DBALTERACAO** | Quando usado como proxy de tempo, classificar como timestamp_confiabilidade = TECNICO; tratado como hipótese operacional, não verdade absoluta. |
| **Variante** | Sequência única de atividades (traço) observada em um ou mais casos. |
| **Gargalo (bottleneck)** | Atividade ou recurso que limita o desempenho do processo. |
| **SE2, FK7, FK2, SE5** | Tabelas Protheus: SE2 = títulos, FK7 = eventos/workflow, FK2 = lançamentos (agregado por caso no log), SE5 = melhor evidência bancária. |
| **Mart** | Camada analítica no dbt (case base, event log, ap_operacional). |
| **Int (intermediate)** | Modelo intermediário no dbt. |
| **Staging (stg_)** | Camada de normalização da fonte bruta; 7 campos da chave + demais colunas. |
