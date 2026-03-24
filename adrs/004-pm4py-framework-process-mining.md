# ADR-004: PM4Py como framework inicial de Process Mining

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Escolha da biblioteca para descoberta de processo, análise de variantes e gargalos.

## Contexto

Process Mining requer: (1) descoberta de modelo de processo a partir do event log, (2) análise de variantes (caminhos frequentes), (3) análise de desempenho e gargalos (tempos, filas). A stack do projeto é Python; é desejável uma biblioteca madura, com suporte a formatos padrão (XES, CSV) e algoritmos clássicos (inductive miner, heuristic miner, etc.).

## Decisão

Adotar **PM4Py** como framework inicial de Process Mining em Python. Uso previsto:

- **Leitura de event log**: a partir de DataFrame (BigQuery → pandas/Parquet) ou arquivo XES/CSV.
- **Descoberta**: algoritmos como inductive miner ou heuristic miner para gerar modelo (Petri net, BPMN ou DFG).
- **Variantes**: análise de traços e variantes; identificação de caminhos mais frequentes.
- **Desempenho/gargalos**: análise de tempos (waiting, processing), identificação de gargalos por atividade ou por recurso.

O código ficará em `python/mining/`, com funções que recebem event log (DataFrame) e retornam modelos, métricas ou artefatos; sem acoplamento a UI ou serviços externos nesta fase.

## Consequências

- **Positivas**: Biblioteca amplamente usada, documentação e exemplos disponíveis; integração natural com pandas; licença open source (Apache 2.0).
- **Negativas**: Curva de aprendizado; algumas funcionalidades avançadas podem exigir versões específicas ou workarounds.
- **Riscos**: Mudanças de API em versões futuras; mitigação: fixar versão em requirements e testar upgrades.

## Alternativas consideradas

1. **ProM (Java)**: Rejeitado; stack do projeto é Python; integração seria via export/import de arquivos, aumentando complexidade operacional.
2. **Celonis/ProcessGold (SaaS)**: Rejeitado para o laboratório; objetivo é capacidade interna e reutilizável; soluções comerciais podem ser avaliadas depois.
3. **Implementação própria**: Rejeitado; PM4Py já implementa algoritmos consagrados; esforço seria desproporcional.
