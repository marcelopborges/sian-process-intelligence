# ADR-009: Camada semântica mínima e iterativa (laboratório)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Define **quanto de “semântica de negócio”** formalizar antes de ter produto fechado. Adequado à fase de estudo: evitar paralisia por catálogo completo, sem abdicar de nomes estáveis onde o mining e a IA precisam.

## Contexto

Uma camada semântica rica (métricas certificadas, hierarquias, ferramentas de BI) exige consenso institucional que o laboratório ainda pode não ter. Ao mesmo tempo, atividades e chaves precisam de convenções mínimas para experimentos reprodutíveis.

## Decisão (direção de trabalho)

Adotar **semântica mínima e incremental**:

- **Mínima**: o necessário para o recorte em estudo (ex.: nomes de atividades, `case_id`, atributos essenciais, convenções no dbt e no glossário).
- **Iterativa**: ampliar quando um uso concreto aparecer (novo relatório, novo processo, integração com BI).

Ferramentas dedicadas de semantic layer podem ser avaliadas **depois**; no estudo, a semântica vive em documentação, comentários de modelo e código em `src/app/`.

## Consequências

- **Esperadas**: Menos bloqueio para experimentar; evolução guiada por necessidade.
- **Cuidados**: Possível retrabalho de nomenclatura — mitigar com glossário e revisão em mudanças relevantes.

## Alternativas consideradas

1. **Catálogo semântico completo no início**: Descartado no estudo por custo de alinhamento.
2. **Apenas nomes técnicos**: Insuficiente para comunicação com negócio e para IA.
3. **Adotar já uma ferramenta de semantic layer**: Adiada até haver demanda clara.
