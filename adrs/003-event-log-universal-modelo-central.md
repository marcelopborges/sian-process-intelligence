# ADR-003: Event log universal como modelo central (alvo de modelagem)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Define um **alvo de desenho** para o mart de eventos durante o estudo. Colunas e regras podem mudar conforme validação com dados reais e negócio; nada aqui é especificação fechada de produção.

## Contexto

Process Mining e simulação assumem um **event log**: eventos por caso com atividade e tempo. Diferentes processos têm tabelas fonte distintas; o estudo beneficia-se de um **padrão de saída** para reutilizar código Python (`src/app/mining`, `src/app/simulation`) e comparar processos.

## Decisão (direção de trabalho)

Trabalhar em direção a um **modelo de event log comum** produzido pelo dbt e consumido pelo código em `src/app/`:

- **Mínimo conceitual**: `case_id`, `activity`, timestamp efetivo para ordenação (no estudo de CP: convenções como `event_timestamp_adjusted` documentadas no domínio).
- **Recomendado**: atributos de caso e de evento conforme necessidade de análise; nomenclatura de atividades alinhada ao glossário em evolução.

O event log é a **base** para experimentos de mining e simulação; a IA, quando usada, interpreta resultados derivados, não substitui o mart.

## Consequências

- **Esperadas**: Código de mineração menos acoplado a um único SQL de origem.
- **Cuidados**: Qualidade de timestamp e de nomes de atividade continua sendo risco — mitigação no estudo: testes dbt e validações em Python.

## Alternativas consideradas

1. **Formato totalmente diferente por processo**: Mais código duplicado no estudo.
2. **Só XES**: Menos natural para BigQuery/dbt; export XES pode ser etapa posterior em Python.
3. **Event log só em memória/script**: Perde rastreabilidade no warehouse durante o estudo.

---

## Nota sobre Contas a Pagar (estudo)

Detalhes de colunas (timestamps original/ajustado, confiabilidade, ordem de eventos) são **hipóteses de modelagem** documentadas em `docs/` e no projeto dbt; devem ser tratados como evolutivos até validação formal.
