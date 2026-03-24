# ADR-001: Repositório dedicado para Process Intelligence

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Decisão sobre onde hospedar o desenvolvimento de Process Intelligence no ecossistema SIAN.

## Contexto

A organização possui (ou planeja) repositórios como **Cortex** (orquestração) e **Argos** (observabilidade). Process Intelligence envolve: modelagem analítica de processos, event logs, mineração (PM4Py), simulação (SimPy) e integração de IA para interpretação e recomendações. É uma capability transversal que pode servir vários produtos e pipelines.

Colocar todo o código e modelos dentro do Cortex ou do Argos traria acoplamento forte a preocupações específicas desses sistemas (orquestração e observabilidade) e dificultaria evolução independente, reuso por outros times e clareza de responsabilidades.

## Decisão

Criar um **repositório dedicado** chamado **sian-process-intelligence** para toda a capability de Process Intelligence (dbt, Python mining/simulation/ai, documentação, prompts e ADRs). O repositório será tratado como um produto técnico reutilizável e, no início, como laboratório estruturado.

Cortex e Argos **não** serão dependências diretas neste estágio; a integração futura será feita por contratos bem definidos (APIs, eventos ou artefatos compartilhados).

## Consequências

- **Positivas**: Responsabilidade clara, evolução independente, reuso por outros projetos, ciclo de release desacoplado, ADRs e documentação focados em Process Intelligence.
- **Negativas**: Mais um repositório para manter; necessidade de definir interfaces quando integrar com Cortex/Argos.
- **Riscos**: Duplicação de convenções (lint, testes, CI) se não houver padrões organizacionais; mitigação: alinhar com práticas comuns e documentar neste repo.

## Alternativas consideradas

1. **Tudo no Cortex**: Rejeitado por misturar orquestração com modelagem de processo e análise; Cortex não deve virar monolito de analytics.
2. **Tudo no Argos**: Rejeitado; Argos foca em observabilidade, não em mineração e simulação de processos.
3. **Múltiplos repos por subdomínio (um para dbt, um para Python)**: Rejeitado no início para evitar fragmentação excessiva; um repo com estrutura clara (dbt/, python/, docs/) atende melhor a fase de laboratório.
