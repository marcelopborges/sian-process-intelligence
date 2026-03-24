# ADR-010: Separação entre case_base, event_log e análise inteligente

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Organização lógica dos artefatos de dados e da camada de análise.

## Contexto

Os dados de processo podem ser representados em níveis diferentes: (1) uma visão por **caso** (uma linha por título a pagar, por exemplo), com atributos agregados; (2) uma visão por **evento** (uma linha por atividade executada no caso), que forma o event log; (3) **análises** derivadas (variantes, gargalos, recomendações) que consomem o event log ou o case base. Misturar esses níveis em uma única tabela ou pipeline dificulta manutenção, testes e reuso (ex.: mining só precisa do event log; relatório gerencial pode usar case base).

## Decisão

Separar claramente três camadas de artefatos:

1. **Case base** (mart): uma linha por caso de processo (ex.: por documento/título em Contas a Pagar), com atributos de caso (filial, fornecedor, valor, datas de início/fim, duração, etc.). Usado para relatórios gerenciais, KPIs por caso e como entrada para enriquecer o event log com atributos de caso.
2. **Event log** (mart): uma linha por evento (atividade + timestamp + case_id + atributos necessários). Usado exclusivamente por Process Mining (PM4Py) e como base para simulação (parâmetros). É a **fonte de verdade** para descoberta de fluxo, variantes e gargalos.
3. **Análise inteligente**: resultados e metadados produzidos pela camada de mining, simulação e IA (ex.: variantes identificadas, gargalos, sumários, recomendações). Podem ser armazenados em tabelas, arquivos ou expostos via API no futuro; **não** substituem case base nem event log como fonte primária.

No dbt: marts distintos (`mart_cp_case_base`, `mart_cp_event_log`). No Python: leitura do event log (e opcionalmente do case base) em `connectors` ou `core`; mining e simulação produzem resultados; a camada `ai` consome esses resultados para interpretação e recomendação, sem reescrever dados de processo.

## Consequências

- **Positivas**: Responsabilidades claras; testes e auditoria por camada; reuso (ex.: outro processo só precisa replicar a estrutura de case base e event log).
- **Negativas**: Mais uma tabela (case base) para manter; necessidade de garantir consistência entre case base e event log (ex.: mesmo case_id, mesmas convenções).
- **Riscos**: Duplicação de lógica entre case base e event log se não houver reuso de CTEs no dbt; mitigação: int models compartilhados e marts que referenciam os mesmos int.

## Alternativas consideradas

1. **Apenas event log (sem case base)**: Rejeitado; relatórios por caso e KPIs agregados são mais simples com uma tabela de caso; event log pode ser enriquecido com join ao case base.
2. **Uma única tabela "processo" com nível evento e atributos de caso repetidos**: Rejeitado; redundância e confusão entre granularidade de caso e de evento.
3. **Análise inteligente escrita de volta no BigQuery como "fonte"**: Rejeitado; análises são derivadas; a fonte primária permanece case base e event log produzidos pelo dbt.

---

## Decisões subsequentes (Contas a Pagar)

- **Case base**: materialização TABLE; estático e reprodutível; sem CURRENT_DATE() em status_macro/status_detalhado. Inclui status_macro, status_detalhado, tem_fk7, tem_se5, fonte_dt_pagamento, vl_pago_consolidado, vl_pago_e_inferido. Não usar COALESCE de forma a mascarar ausência de SE5 como fato bancário.
- **Event log**: materialização TABLE; event_timestamp_original, event_order, event_timestamp_adjusted, timestamp_confiabilidade (coluna explícita). Ordenação lógica para desempate (1-7 por atividade).
- **Terceira saída**: mart_cp_ap_operacional (VIEW), camada operacional/dinâmica; aqui podem existir cálculos com CURRENT_DATE() (aging, vencidos, SLA). Não usar para Process Mining.
- Detalhes em docs/architecture.md e docs/domain-contas-a-pagar.md.
