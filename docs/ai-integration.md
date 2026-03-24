# Integração de IA — Visão geral

A IA no projeto atua como **amplificador** da análise, não como fonte primária de dados ou métricas (ADR-006). Este documento resume onde a IA entra e onde não entra; detalhes por fase estão em `docs/ai-strategy.md`.

## Onde a IA ajuda

- **Documentação**: geração de texto descritivo a partir de modelos e métricas já definidos.
- **Interpretação**: explicar variantes e gargalos em linguagem natural para executivos.
- **Sumarização**: resumos executivos a partir de resultados de mining e simulação.
- **Recomendações**: sugestões de melhoria baseadas em dados (ex.: “atividade X concentra Y% do tempo de espera”).
- **Copiloto**: auxílio em SQL, mapeamento de eventos e revisão de documentação (uso em desenvolvimento).

## Onde a IA não substitui

- **Modelagem de dados**: definição de tabelas, colunas e regras de negócio (dbt e negócio).
- **Métricas oficiais**: tempo de ciclo, quantidade de casos, variantes — vêm do pipeline (dbt + PM4Py/SimPy).
- **Validação de qualidade**: regras de teste e auditoria são determinísticas.
- **Decisão final**: recomendações da IA são insumos; a decisão é humana.

## Guardrails

- Prompts devem receber **contexto explícito** (ex.: “com base nos seguintes resultados de mineração”).
- Instruções para o modelo: não inventar números; citar origem dos dados quando relevante.
- Dados sensíveis: não enviar para APIs externas sem política de privacidade; preferir modelos internos quando houver.

## Oportunidades de produto

- Relatórios executivos gerados a partir de um clique sobre o event log.
- “Assistente de processo” que responde perguntas sobre variantes e gargalos usando os marts.
- Futuro: agente que executa mining/simulação sob demanda e devolve interpretação (integração com Cortex).

## Riscos

- **Alucinação**: modelo inventar métricas ou conclusões; mitigação: sempre passar dados reais no prompt e validar amostras.
- **Dependência**: over-reliance em texto da IA; mitigação: treinamento de uso e exibir sempre a base de dados (tabela, métrica).
- **Custo e latência**: chamadas a LLM; mitigação: cache onde fizer sentido e uso de modelos menores para tarefas simples.
