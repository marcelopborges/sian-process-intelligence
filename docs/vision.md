# Visão do produto — SIAN Process Intelligence

## Visão geral

O **SIAN Process Intelligence** é uma capability de análise e melhoria de processos organizacionais a partir de dados já existentes no ecossistema (BigQuery). Começa como laboratório estruturado com foco em **Contas a Pagar** no TOTVS Protheus e evolui para outros processos (Compras, RH, Controladoria) e para integração com Cortex e Argos.

## Problema

- Processos críticos (contas a pagar, compras, etc.) geram dados em várias tabelas e sistemas, sem uma visão unificada de **fluxo**, **tempo** e **variantes**.
- Decisões de melhoria são muitas vezes baseadas em percepção, não em evidência quantitativa (onde estão os gargalos? quantas variantes existem? qual o impacto de mais um recurso?).
- Documentação de processos e análises consome tempo e fica desatualizada; há espaço para **IA como amplificador** (interpretação, sumarização, recomendações), sem substituir a modelagem de dados.

## Proposta de valor

1. **Tabelas analíticas de processo** (case base + event log) construídas de forma versionada e testável (dbt) no BigQuery.
2. **Process Mining** (descoberta de fluxo, variantes, gargalos) com PM4Py, consumindo o event log.
3. **Simulação** de cenários (SimPy) para estimar impacto de mudanças antes de implementar.
4. **Camada de IA** para interpretação, sumarização executiva e recomendações, sempre baseada nos dados e métricas produzidos pelo pipeline (não como fonte de verdade).

## Princípios

- **Dados como verdade**: métricas e regras vêm do dbt e dos algoritmos de mining/simulação; a IA interpreta e comunica.
- **Capability reutilizável**: arquitetura preparada para vários processos e para futura integração com orquestração (Cortex) e observabilidade (Argos).
- **Iteração**: começar com escopo mínimo (Contas a Pagar, camada semântica mínima) e expandir conforme validação com negócio.
- **Rastreabilidade**: ADRs para decisões; documentação e glossário centralizados.

## Escopo inicial vs futuro

| Inicial | Futuro |
|--------|--------|
| Contas a Pagar (SE2 → FK7 → FK2 → SE5) | Compras, RH, Controladoria |
| dbt + Python (mining, simulação) | Integração Cortex/Argos |
| IA: interpretação e recomendações em fases | Agente analista de processos |
| Laboratório / produto interno | Produto exposto para outras áreas |

## Sucesso

- Case base e event log de Contas a Pagar publicados e validados com área de negócio.
- Pipeline de mining (variantes, gargalos) rodando e gerando insights acionáveis.
- Pelo menos um cenário de simulação documentado e replicável.
- Primeiros prompts de IA (interpretação/sumarização) em uso, com guardrails claros.
