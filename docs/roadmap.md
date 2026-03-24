# Roadmap — SIAN Process Intelligence

Visão de fases para desenvolvimento e entrega. Ajustar conforme prioridades e capacidade.

## Fase 0 — Bootstrap (concluída)

- Estrutura do repositório (pastas, README, .gitignore, config).
- ADRs 001 a 010.
- Documentação inicial (vision, architecture, process-intelligence, ai-integration, domain, glossary, roadmap).
- Esqueletos dbt (staging, int, mart) e Python (mining, simulation, ai, connectors, core, utils).
- Prompts e estratégia de IA documentados.

## Fase 1 — Dados e event log

- **Objetivo**: Case base e event log de Contas a Pagar publicados e validados.
- **Entregas**:
  - Staging (stg_se2, stg_fk7, stg_fk2, stg_se5) apontando para tabelas reais no BigQuery.
  - Ajuste dos modelos int com colunas e regras validadas com negócio/Protheus.
  - mart_cp_case_base e mart_cp_event_log com testes dbt (unique, not_null, accepted_values onde aplicável).
  - Documentação de mapeamento de atividades (FK7 → nomes) no glossário.
- **Critério de sucesso**: dbt run e dbt test verdes; amostra de event log validada com área de negócio.

## Fase 2 — Process Mining

- **Objetivo**: Pipeline de mining (discovery, variantes, gargalos) rodando sobre o event log.
- **Entregas**:
  - Connector de leitura do event log (BigQuery e/ou arquivo).
  - Implementação de discovery, variants e bottlenecks em Python (PM4Py).
  - Notebook ou script que gera modelo descoberto, top variantes e top gargalos.
  - Documentação de uso e interpretação dos resultados.
- **Critério de sucesso**: Relatório de variantes e gargalos gerado a partir do mart_cp_event_log (ou amostra).

## Fase 3 — Simulação e IA (interpretação)

- **Objetivo**: Primeiro cenário de simulação e primeiros textos assistidos por IA.
- **Entregas**:
  - Modelo SimPy para Contas a Pagar (recursos, tempos, filas) e script de execução.
  - Parâmetros estimados a partir do event log (ou configuráveis).
  - Integração mínima com LLM (abstração em ai/llm_client).
  - Prompts de interpretação de variantes e gargalos e de sumarização executiva em uso.
- **Critério de sucesso**: Um cenário de simulação documentado; um sumário executivo gerado por IA a partir de resultados reais.

## Fase 4 — Recomendações e preparação para integração

- **Objetivo**: Recomendações assistidas por IA e contrato para Cortex/Argos.
- **Entregas**:
  - Geração de recomendações a partir de mining (e opcionalmente simulação) com guardrails.
  - Documentação de contratos (tabelas, formatos, triggers) para integração com Cortex e Argos.
  - (Opcional) Protótipo de agente analista (consultas + mining + interpretação) para uso interno.
- **Critério de sucesso**: Fluxo “mining → recomendações” validado; documento de contrato de integração aprovado.

## Próximos passos imediatos

1. Validar com donos dos dados que SE2, FK7, FK2, SE5 estão (ou estarão) no BigQuery e obter nomes de dataset/tabela.
2. Implementar stg_* com source real e rodar dbt run/test.
3. Ajustar int e mart com regras de negócio (filtros, mapeamento de atividades) e rodar primeira análise de variantes em notebook.
