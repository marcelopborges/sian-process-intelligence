# ADR-006: IA como camada de interpretação e recomendação (não como verdade primária)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Princípio de **uso responsável de LLMs** durante o laboratório. Não restringe pesquisa futura; fixa expectativa: dados e regras auditáveis primeiro, texto e sugestões depois.

## Contexto

LLMs podem ajudar em documentação, sumários e explicações sobre resultados de mining. Ao mesmo tempo, métricas oficiais e definições de processo precisam ser rastreáveis em ambiente de estudo e, mais ainda, em produção futura.

## Decisão (direção de trabalho)

Posicionar **IA como camada sobre artefatos já produzidos** (dbt, PM4Py, SimPy, relatórios):

- **Papel típico**: linguagem natural, sugestões, copiloto; eventual agente com supervisão.
- **Não papel**: fonte única de números ou regras de negócio não reproduzíveis.

Implementações experimentais devem concentrar-se em **`src/app/ai/`** e em `prompts/`, com guardrails claros nos prompts (não inventar métricas; citar origem quando possível).

## Consequências

- **Esperadas**: Menor risco de confundir “texto gerado” com “dado de sistema”.
- **Cuidados**: Usuários do estudo ainda devem ser treinados a validar saídas de IA.

## Alternativas consideradas

1. **IA como fonte de métricas**: Inadequada ao objetivo de auditoria.
2. **Sem IA no escopo**: Possível, mas o ADR registra que há valor em documentação assistida quando bem delimitada.
3. **Pipeline totalmente generativo**: Rejeitada para o estudo por fragilidade de auditoria.
