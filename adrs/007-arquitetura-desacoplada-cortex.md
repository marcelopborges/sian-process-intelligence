# ADR-007: Arquitetura desacoplada, pronta para futura integração com Cortex

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Relação deste repositório com o Cortex (e com Argos) e como evitar acoplamento prematuro.

## Contexto

O **Cortex** é (ou será) o sistema de orquestração de pipelines e serviços no ecossistema SIAN. O **sian-process-intelligence** implementa uma capability (Process Intelligence) que no futuro pode ser invocada pelo Cortex (ex.: rodar mining sob demanda, expor métricas, disparar simulações). Integrar desde o início criaria dependência de um sistema que pode ainda estar em evolução e aumentaria a complexidade do laboratório.

## Decisão

Manter **arquitetura desacoplada**: este repositório não depende do Cortex nem do Argos em tempo de build ou execução. Contratos e interfaces serão desenhados de forma que:

- **Entradas**: o projeto assume que dados estão no BigQuery e que event logs/case bases são produzidos pelo dbt; não há chamadas HTTP ou SDK ao Cortex para obter dados.
- **Saídas**: resultados (tabelas, arquivos, métricas) ficam em BigQuery ou em artefatos definidos (ex.: diretório de output); o Cortex pode, no futuro, orquestrar jobs que rodam dbt e Python e consumir esses artefatos.
- **Configuração**: uso de variáveis de ambiente e arquivos de config (ex.: `.env`, `config/`) para credenciais e endpoints; quando houver integração, um adapter em `python/connectors/` ou em um serviço separado poderá chamar Cortex/Argos sem que o núcleo do Process Intelligence dependa deles.

A documentação (README, docs/architecture.md) deve explicitar essa decisão e descrever o ponto de extensão para integração futura (APIs, eventos, convenções de artefatos).

## Consequências

- **Positivas**: Desenvolvimento e testes independentes; menor risco de bloqueio por mudanças no Cortex; integração pode ser feita quando os contratos estiverem estáveis.
- **Negativas**: Duplicação possível de conceitos (ex.: agendamento) até a integração; necessidade de documentar o "contrato" futuro.
- **Riscos**: Divergência de convenções (nomenclatura, formato de dados) entre este repo e o Cortex; mitigação: definir e documentar contratos de interface antes da implementação da integração.

## Alternativas consideradas

1. **Integrar ao Cortex desde o início**: Rejeitado; Cortex pode não estar pronto; escopo do laboratório é validar Process Intelligence, não orquestração.
2. **Não planejar integração**: Rejeitado; deixar claro o ponto de extensão reduz retrabalho quando a organização decidir integrar.
3. **Criar um "mini-orquestrador" neste repo**: Rejeitado para a fase inicial; Makefile e scripts são suficientes; orquestração completa fica com o Cortex.
