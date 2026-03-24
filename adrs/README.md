# Architecture Decision Records (ADRs)

Este diretório registra **direções de trabalho e hipóteses** do projeto **sian-process-intelligence**, no formato ADR (contexto, decisão, consequências, alternativas).

## Vigência e status

O repositório está em **fase de estudo e laboratório**. Os ADRs descrevem o raciocínio atual e o desenho pretendido; **não constituem política corporativa nem compromisso de produção** até serem formalmente adotados por governança de arquitetura ou produto. Podem ser revisados ou substituídos à medida que o estudo avança.

Decisão de **núcleo único Python** (`src/app`): ver também [ADR-011 em docs/adrs](../docs/adrs/ADR-011-core-architecture-src-app.md).

## Índice

| Número | Título |
|--------|--------|
| 011 | [Núcleo oficial em `src/app` (docs/)](../docs/adrs/ADR-011-core-architecture-src-app.md) |
| 001 | [Repositório dedicado para Process Intelligence](001-repositorio-dedicado-process-intelligence.md) |
| 002 | [BigQuery + dbt como fundação analítica](002-bigquery-dbt-fundacao-analitica.md) |
| 003 | [Event log universal como modelo central](003-event-log-universal-modelo-central.md) |
| 004 | [PM4Py como framework de Process Mining](004-pm4py-framework-process-mining.md) |
| 005 | [SimPy como motor de simulação](005-simpy-motor-simulacao.md) |
| 006 | [IA como camada de interpretação e recomendação](006-ia-camada-interpretacao-recomendacao.md) |
| 007 | [Arquitetura desacoplada para futura integração Cortex](007-arquitetura-desacoplada-cortex.md) |
| 008 | [Processo inicial: Contas a Pagar no Protheus](008-processo-inicial-contas-a-pagar.md) |
| 009 | [Camada semântica mínima iterativa](009-camada-semantica-minima-iterativa.md) |
| 010 | [Separação case_base, event_log e análise inteligente](010-separacao-case-base-event-log-analise.md) |

## Convenção

- Nome do arquivo: `NNN-kebab-case-titulo.md`
- Estrutura sugerida: Contexto, Decisão (direção de trabalho), Consequências, Alternativas consideradas, Status e vigência.
