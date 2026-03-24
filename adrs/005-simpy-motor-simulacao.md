# ADR-005: SimPy como motor inicial de simulação

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Necessidade de simular cenários de processo (recursos, tempos, filas) para análise what-if.

## Contexto

Além de mineração (o que aconteceu), é importante simular **cenários** (e.g. mais um analista, redução de tempo em uma etapa, mudança de prioridade) para estimar impacto em tempo de ciclo, utilização e filas. A simulação deve ser baseada em dados reais (distribuições ou parâmetros extraídos do event log) quando possível, com modelo discreto por eventos (DES).

## Decisão

Adotar **SimPy** como motor de simulação discreta por eventos em Python. Uso previsto:

- **Modelo de processo**: atividades, recursos (ex.: analistas, aprovadores), filas e tempos (distribuições ou constantes derivadas do event log).
- **Cenários**: variação de número de recursos, tempos médios, regras de prioridade; execução de N replicações para obter métricas (tempo de ciclo, throughput, utilização).
- **Integração**: parâmetros podem ser estimados a partir da camada de mining (estatísticas por atividade); resultados da simulação alimentam relatórios e, futuramente, a camada de IA para recomendações.

O código ficará em `python/simulation/`, desacoplado do PM4Py na interface pública (podem compartilhar leitura de event log via `core` ou `connectors`).

## Consequências

- **Positivas**: SimPy é leve, puro Python, bem documentado; modelo DES adequado para processos de negócio; alinhado com stack Python.
- **Negativas**: Construção do modelo de simulação a partir do processo real exige mapeamento e calibração; responsabilidade do time de produto/negócio validar premissas.
- **Riscos**: Modelo simplificado demais pode gerar resultados enganosos; documentar premissas e limites em cada cenário.

## Alternativas consideradas

1. **Arena / AnyLogic**: Rejeitado para o laboratório; ferramentas proprietárias e não integradas ao repositório Python; possível avaliação futura para usuários de negócio.
2. **Simulação dentro do PM4Py**: PM4Py foca em mining; simulação é escopo diferente; SimPy é mais flexível para DES customizado.
3. **Outra lib Python (salabim, etc.)**: SimPy é a mais difundida e suficiente para o escopo; outras podem ser avaliadas se houver necessidade específica.
