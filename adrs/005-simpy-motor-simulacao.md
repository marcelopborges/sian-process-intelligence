# ADR-005: SimPy como motor de simulação (experimento)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Define intenção de usar **simulação discreta** para cenários what-if no laboratório. Modelos de simulação não são calibrados para decisão operacional até validação explícita com negócio.

## Contexto

Além de descrever o que ocorreu (mining), o estudo pode explorar **cenários** (recursos, tempos, filas). Simulação discreta por eventos (DES) em Python é compatível com a stack do repo.

## Decisão (direção de trabalho)

Adotar **SimPy** como motor inicial de simulação. Código relacionado deve residir em **`src/app/simulation/`**, desacoplado da interface pública do PM4Py (podendo compartilhar leitura de event log via `src/app/core` ou `src/app/connectors`).

## Consequências

- **Esperadas**: Protótipos leves em Python; boa documentação da lib.
- **Cuidados**: Qualquer número de simulação é sensível a premissas — documentar limites em cada experimento.

## Alternativas consideradas

1. **Ferramentas proprietárias (Arena, etc.)**: Fora do repo; possível comparação futura.
2. **Simulação dentro do PM4Py**: Escopo distinto; SimPy oferece flexibilidade para DES customizado no estudo.
3. **Outras libs Python**: SimPy permanece candidata padrão até surgir necessidade específica.
