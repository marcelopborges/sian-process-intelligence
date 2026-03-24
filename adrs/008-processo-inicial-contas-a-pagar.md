# ADR-008: Primeiro recorte de estudo — Contas a Pagar no Protheus

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Escolha do **primeiro domínio** para experimentar pipeline (dbt → event log → análises). Reflete prioridade de pesquisa, não contrato de produto nem cobertura de todos os módulos Protheus.

## Contexto

Para validar a stack e o modelo mental de event log, o estudo precisa de um processo concreto com dados acessíveis e relevância de negócio. **Contas a Pagar** oferece cadeia de tabelas conhecida e impacto financeiro.

## Decisão (direção de trabalho)

Usar **Contas a Pagar** como recorte inicial no TOTVS Protheus, com foco na cadeia de referência:

- **SE2**, **FK7**, **FK2**, **SE5** (papéis descritos em documentação de domínio em evolução).

Isso orienta:

- Modelos dbt em `dbt/` (nomes como `int_cp_*`, marts de CP).
- Documentação e glossário em `docs/`.
- Pipelines semânticos experimentais em `src/app/discovery`, `src/app/pipeline`, etc.

A estrutura do repositório (`src/app/`) permanece **genérica** para permitir outros processos no futuro sem reescrita total.

## Consequências

- **Esperadas**: Foco e aprendizado acumulado em um fluxo completo.
- **Cuidados**: Customizações do Protheus podem alterar campos e regras; tudo deve ser tratado como hipótese até validação com dados e especialistas.

## Alternativas consideradas

1. **Outro processo primeiro (Compras, RH)**: Adiado para depois de estabelecer padrão com CP.
2. **Dados sintéticos apenas**: Menos valor para validar com negócio; o estudo prioriza realidade.
3. **Vários processos em paralelo no início**: Evitado para reduzir dispersão no laboratório.

---

## Nota

Regras finas (definição de caso, chaves, tratamento de valores e datas) são **detalhes de modelagem em evolução**; ver documentação de domínio e modelos dbt, sempre como trabalho em andamento.
