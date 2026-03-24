# ADR-001: Repositório dedicado para Process Intelligence

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Decisão de **organização de código e colaboração** no contexto de laboratório. Não define onde sistemas oficiais rodarão em produção; apenas que o trabalho de Process Intelligence neste ciclo se concentra neste repositório.

## Contexto

No ecossistema SIAN podem existir iniciativas como **Cortex** (orquestração) e **Argos** (observabilidade). Process Intelligence envolve modelagem analítica, event logs, mineração, simulação e eventual uso de IA para interpretação — uma capability transversal. Durante o estudo, importa evitar misturar essas preocupações com orquestração ou observabilidade antes de haver contratos claros.

## Decisão (direção de trabalho)

Manter um **repositório dedicado** (**sian-process-intelligence**) como lugar do estudo: dbt, código Python em `src/app/`, documentação, prompts e estes ADRs. Tratar o repo como **laboratório estruturado**, não como serviço implantado.

Cortex e Argos **não** são dependências de build ou runtime nesta fase; integrações futuras seriam por contratos (APIs, eventos, artefatos), a definir quando o estudo amadurecer.

## Consequências

- **Esperadas**: Responsabilidade de pasta clara; evolução do estudo sem arrastar o Cortex; ADRs focados em PI.
- **Cuidados**: Outro repositório organizacional pode acabar duplicando convenções (lint, CI) — alinhar quando houver decisão de produto.

## Alternativas consideradas (para o estudo)

1. **Tudo no Cortex**: Descartada no laboratório para não misturar orquestração com modelagem.
2. **Tudo no Argos**: Descartada; foco de Argos não é mining/simulação.
3. **Vários repositórios (dbt separado de Python)**: Descartada no início para reduzir fragmentação; monorepo com `dbt/`, `src/app/`, `docs/` atende o estudo.
