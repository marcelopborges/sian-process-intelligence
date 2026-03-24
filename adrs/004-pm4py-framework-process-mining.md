# ADR-004: PM4Py como framework de Process Mining (laboratório)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Escolha de **biblioteca padrão para experimentos** de mining no Python. Outras ferramentas (comerciais ou outras libs) podem ser avaliadas depois sem invalidar o estudo de domínio e de dados.

## Contexto

O estudo precisa de descoberta de modelo, variantes e análise de desempenho a partir de event log. A stack em discussão é Python; PM4Py é uma opção madura e documentada.

## Decisão (direção de trabalho)

Usar **PM4Py** como ponto de partida para Process Mining no repositório. Código de exploração e funções futuras devem viver em **`src/app/mining/`**, recebendo event log (DataFrame ou arquivos) e devolvendo artefatos de análise, sem acoplamento a UI ou a serviços externos nesta fase.

## Consequências

- **Esperadas**: Exemplos e literatura abundantes; integração com pandas.
- **Cuidados**: Versão da lib deve ser fixada no ambiente de estudo; APIs podem mudar entre major versions.

## Alternativas consideradas

1. **ProM (Java)**: Descartada para o estudo atual pela stack preferida ser Python.
2. **SaaS comercial**: Pode coexistir no futuro como comparação; não é premissa do laboratório inicial.
3. **Implementação própria dos algoritmos**: Descartada por custo frente ao escopo de estudo de processo de negócio.
