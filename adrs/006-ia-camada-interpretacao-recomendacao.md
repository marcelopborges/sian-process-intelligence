# ADR-006: IA como camada de interpretação e recomendação, não como fonte primária de verdade

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Papel da IA (LLMs e ferramentas generativas) no produto de Process Intelligence.

## Contexto

A IA pode auxiliar em documentação, interpretação de variantes e gargalos, sumarização executiva e geração de recomendações. Por outro lado, métricas, regras de negócio e definição de atividades devem ser determinísticas e auditáveis. Usar IA como "fonte de verdade" para dados ou regras introduz riscos de alucinação, inconsistência e dificuldade de auditoria.

## Decisão

Tratar **IA como camada de interpretação e recomendação** sobre artefatos já produzidos pela pipeline de dados e mining:

- **Onde a IA atua**: geração de texto (documentação, sumários, explicações de variantes/gargalos, recomendações em linguagem natural); sugestões de SQL ou mapeamentos (como copiloto); futuramente, agente que consulta dados e ferramentas com supervisão.
- **Onde a IA não substitui**: definição de modelo de dados (dbt); regras de negócio para atividades e casos; métricas oficiais (tempo de ciclo, quantidade de casos); validação de qualidade dos dados.

Ou seja: **dados e métricas vêm do dbt e do PM4Py/SimPy; a IA interpreta e comunica**, não inventa números nem regras. Prompts e integrações devem deixar claro o contexto (ex.: "com base nos seguintes resultados de mineração...") e, quando aplicável, incluir guardrails (não inventar métricas, citar origem).

## Consequências

- **Positivas**: Rastreabilidade e auditoria preservadas; menor risco de decisões baseadas em alucinações; evolução da IA em fases (copiloto → interpretação → recomendações → agente) sem comprometer a base analítica.
- **Negativas**: Limitação do que a IA pode "decidir" sozinha; fluxos que exigem aprovação humana para recomendações.
- **Riscos**: Uso indevido de saídas da IA como verdade; mitigação: documentação clara, exemplos de prompts em `prompts/` e treinamento de uso.

## Alternativas consideradas

1. **IA como fonte de métricas (ex.: "quantos casos?")**: Rejeitado; métricas devem vir de queries e mining reproduzíveis.
2. **Sem IA no escopo**: Rejeitado; há valor claro em documentação assistida e interpretação; a decisão é *como* integrar, não *se* integrar.
3. **IA end-to-end (da raw ao relatório)**: Rejeitado; inviabilizaria auditoria e reprodutibilidade da base analítica.
