# ADR-008: Começar pelo processo de Contas a Pagar no Protheus

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Escolha do primeiro processo de negócio para implementar o pipeline de Process Intelligence.

## Contexto

É necessário escolher um processo concreto para validar a stack (dbt → event log → PM4Py/SimPy → IA). O processo deve ter dados disponíveis no Protheus (ou já carregados no BigQuery), relevância para o negócio e uma cadeia de tabelas identificável para mapear atividades e timestamps. Contas a Pagar é um processo crítico, com impacto em fluxo de caixa e controles, e possui uma sequência conhecida no Protheus.

## Decisão

Iniciar pelo processo de **Contas a Pagar** no TOTVS Protheus, utilizando a cadeia de tabelas:

- **SE2**: títulos a pagar (origem do caso).
- **FK7**: eventos/estados relacionados ao título (ex.: aprovações, eventos de workflow).
- **FK2**: lançamentos contábeis (movimentações).
- **SE5**: pagamentos (encerramento do fluxo de pagamento).

Essa sequência (SE2 → FK7 → FK2 → SE5) será a base para:

- Modelos dbt: `int_cp_*` e marts `mart_cp_case_base`, `mart_cp_event_log`.
- Definição de atividades (ex.: Emissão Título, Análise, Aprovação, Lançamento, Pagamento) a ser refinada com negócio.
- Primeiros pipelines de mining e simulação e documentação de domínio em `docs/domain-contas-a-pagar.md`.

A arquitetura do repositório (estrutura de pastas, modelo de event log, módulos Python) deve permanecer genérica para permitir inclusão futura de outros processos (Compras, RH, Controladoria) sem reestruturação completa.

## Consequências

- **Positivas**: Foco claro; domínio conhecido; possibilidade de validar com áreas financeiras; padrão replicável para outros processos.
- **Negativas**: Regras específicas do Protheus (nomes de campos, chaves) precisam ser validadas com quem conhece o sistema; possível necessidade de ajustes ao descobrir particularidades das tabelas.
- **Riscos**: Cadeia SE2/FK7/FK2/SE5 pode ter variações por versão ou customização do Protheus; documentar premissas e validar com dados reais.

## Alternativas consideradas

1. **Compras ou RH primeiro**: Rejeitado para o primeiro ciclo; Contas a Pagar tem cadeia bem documentada e alto impacto; outros processos seguem depois.
2. **Processo genérico "demo"**: Rejeitado; um processo real permite validar com negócio e identificar requisitos de dados e nomenclatura.
3. **Múltiplos processos em paralelo**: Rejeitado no início; um processo bem feito estabelece o padrão e reduz dispersão.

---

## Decisões subsequentes (modelagem consolidada)

- **Definição formal do caso**: 1 caso = 1 título financeiro SE2. Case ID = chave composta de 7 campos com TRIM: E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA, E2_TIPO, E2_FORNECE, E2_LOJA. Documentado no modelo e em docs/domain-contas-a-pagar.md.
- **Três saídas distintas**: mart_cp_case_base (TABLE, estático), mart_cp_event_log (TABLE, mining), mart_cp_ap_operacional (VIEW, dinâmica para aging/SLA). Status no case base estático; lógica com CURRENT_DATE() apenas na camada operacional.
- **Valor**: separar valor observado (SE2, SE5) de inferido; flag vl_pago_e_inferido. FK7 como elo do evento financeiro; FK2 agregado por caso; SE5 como melhor evidência bancária. DBALTERACAO tratado como TECNICO, não verdade absoluta.
- Detalhes em docs/domain-contas-a-pagar.md e docs/glossary.md.
