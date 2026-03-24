# Domínio — Contas a Pagar (Protheus)

## Objetivo

Documentar o processo de **Contas a Pagar** no TOTVS Protheus no escopo deste projeto: definição formal do caso, chave composta, tabelas envolvidas, atividades do event log, regras de valor e camadas (case base vs event log vs operacional).

## Definição formal do caso

**1 caso = 1 título financeiro SE2.**

O case_id é a chave composta de **7 campos** (nomes Protheus), com TRIM nos componentes textuais para evitar colisão por espaços:

- E2_FILIAL
- E2_PREFIXO
- E2_NUM
- E2_PARCELA
- E2_TIPO
- E2_FORNECE
- E2_LOJA

No dbt, a macro `cp_case_id` monta o case_id a partir desses campos. O join de FK7, FK2 e SE5 com a SE2 deve usar a mesma chave de 7 campos.

## Tabelas Protheus (cadeia SE2 → FK7 → FK2 → SE5)

| Tabela | Papel no processo |
|--------|-------------------|
| **SE2** | Títulos a pagar. Origem do caso. |
| **FK7** | Eventos/workflow (ex.: liberação, evento financeiro, baixa). Elo do evento financeiro. |
| **FK2** | Lançamentos contábeis. No event log principal: **agregado por caso** (um evento LANCAMENTO_CONTABIL por caso na V1). |
| **SE5** | Pagamentos. **Melhor evidência bancária** quando existir. |

## Separação de camadas

- **Case base** (`mart_cp_case_base`): TABLE, estático e reprodutível. Sem CURRENT_DATE() em status_macro/status_detalhado. Valor observado (SE2, SE5) vs inferido; flag `vl_pago_e_inferido`. Não usar COALESCE de forma a mascarar ausência de SE5 como fato bancário.
- **Event log** (`mart_cp_event_log`): TABLE, focado em Process Mining. Histórico estável. Contém `event_timestamp_original`, `event_order`, `event_timestamp_adjusted`, `timestamp_confiabilidade`.
- **Operacional** (`mart_cp_ap_operacional`): VIEW, dinâmica. Aqui podem existir cálculos com CURRENT_DATE() (aging, vencidos, SLA). Não usar para mining.

## Atividades do event log

Valores padronizados (accepted_values no dbt):

- TITULO_CRIADO
- TITULO_LIBERADO
- EVENTO_FINANCEIRO_GERADO
- LANCAMENTO_CONTABIL
- PAGAMENTO_REALIZADO
- BAIXA_SEM_SE5 (qualquer ocorrência de BAIXA_MANUAL é renomeada para BAIXA_SEM_SE5)
- TITULO_CANCELADO

Ordem lógica para desempate (event_order): 1 a 7 conforme a lista acima; PAGAMENTO_REALIZADO e BAIXA_SEM_SE5 = 5.

## Valor: observado vs inferido

- **Valor do título**: SE2 (ex.: E2_VALOR).
- **Valor bancário observado**: SE5 quando existir (`vl_pago_observado`).
- **Valor consolidado**: `vl_pago_consolidado`; quando não há SE5 mas o título está baixa/pago, pode ser inferido com `vl_pago_e_inferido = true`. Flag explícita para não mascarar inferência.

## Timestamps e confiabilidade

- **event_timestamp_original**: timestamp bruto do evento.
- **event_timestamp_adjusted**: derivado do original com offset por `event_order` (desempate no mesmo dia); usado para ordenação estável no mining.
- **timestamp_confiabilidade**: `NEGOCIO` (data de negócio forte, ex.: emissão, pagamento bancário) ou `TECNICO` (ex.: DBALTERACAO como proxy). Onde DBALTERACAO for usado, classificar como TECNICO; não assumir precisão que não exista.

## Premissas e limites

- Nomes reais de colunas (E2_*, F7_*, F2_*, E5_*) podem variar por versão/customização do Protheus; staging e int devem ser ajustados à fonte real. HYPOTHESIS documentada nos modelos onde houver incerteza.
- DBALTERACAO é hipótese operacional, não verdade absoluta.
- Este documento reflete as decisões consolidadas; revisar com negócio e ambiente real quando necessário.
