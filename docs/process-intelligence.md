# Process Intelligence — Conceitos e uso no projeto

## O que é Process Intelligence

Process Intelligence combina **Process Mining** (o que aconteceu no processo, a partir de dados de evento) com **análise de desempenho** e **simulação** para apoiar melhoria contínua. No este projeto:

1. **Dados de processo**: event log (case_id, activity, timestamp) e case base (atributos por caso).
2. **Process Mining**: descoberta do modelo de processo, variantes (caminhos) e gargalos (tempos, recursos).
3. **Simulação**: cenários what-if (mais recursos, menos tempo em uma etapa) com SimPy.
4. **IA**: interpretação e recomendações em linguagem natural sobre os resultados.

## Cadeia Contas a Pagar (Protheus)

- **SE2**: títulos a pagar (origem do caso).
- **FK7**: eventos/workflow (ex.: aprovações).
- **FK2**: lançamentos contábeis.
- **SE5**: pagamentos.

O dbt transforma essas fontes em `mart_cp_case_base` e `mart_cp_event_log`. O Python lê o event log e aplica PM4Py (mining) e SimPy (simulação).

## Fluxo de uso (previsto)

1. **Preparação**: dados no BigQuery; dbt gera case base e event log.
2. **Mineração**: script ou notebook lê event log, roda discovery/variants/bottlenecks (PM4Py).
3. **Simulação**: parâmetros extraídos do event log ou definidos manualmente; SimPy roda N replicações.
4. **Interpretação**: resultados (variantes, gargalos) são passados à camada de IA para gerar texto executivo ou recomendações.
5. **Consumo**: relatórios, BI ou (futuro) Cortex/Argos consomem tabelas e artefatos.

## Riscos e limites

- **Qualidade dos dados**: timestamps ausentes ou incoerentes prejudicam mining; validar com negócio.
- **Premissas da simulação**: modelo simplificado pode não refletir a realidade; documentar premissas.
- **Nomenclatura**: atividades devem ser estáveis e documentadas (glossário); mudanças quebram comparações.
