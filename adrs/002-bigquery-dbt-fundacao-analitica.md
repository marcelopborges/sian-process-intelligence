# ADR-002: BigQuery + dbt como fundação analítica (hipótese de estudo)

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Hipótese de stack para **transformação e versionamento** de modelos durante o laboratório. A organização pode operar outro lake/warehouse em produção; este ADR não fixa contrato corporativo de dados.

## Contexto

Para estudar Process Intelligence a partir do Protheus (e possíveis fontes futuras), faz sentido ter **transformações versionadas** (SQL, testes, documentação). BigQuery e dbt são candidatos naturais quando o dado analítico já vive ou pode viver no BigQuery.

## Decisão (direção de trabalho)

No âmbito do estudo, adotar **BigQuery** como alvo analítico de referência e **dbt** para modelos (staging → int → mart). O repositório contém projeto em `dbt/`; premissa de trabalho: dados brutos ou staging **acessíveis** ao dbt (origem exata pode variar por ambiente de laboratório).

## Consequências

- **Esperadas**: Modelos reproduzíveis, testes dbt, documentação gerada no fluxo de estudo.
- **Cuidados**: Custo de query no BQ em experimentos; necessidade de credenciais e datasets de teste — típico de laboratório, não de promessa de escala produtiva neste ADR.

## Alternativas consideradas

1. **Apenas scripts SQL soltos**: Menos atrativa para testes e doc automatizada no estudo.
2. **Spark/Databricks**: Pode ser reavaliada se o estudo migrar de plataforma.
3. **Low-code sem código revisável**: Menos alinhada a PR e CI no repositório.
