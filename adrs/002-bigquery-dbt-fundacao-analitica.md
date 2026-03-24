# ADR-002: BigQuery + dbt como fundação analítica

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Escolha da stack de dados e transformação para Process Intelligence.

## Contexto

Os dados do TOTVS Protheus (e de outras fontes futuras) precisam ser transformados em estruturas analíticas: case base (um registro por caso de processo) e event log (eventos por atividade). A organização já utiliza ou planeja utilizar BigQuery como data lake/lakehouse. É necessário um mecanismo de transformação versionado, testável e documentado.

## Decisão

Adotar **BigQuery** como armazenamento analítico e **dbt** como ferramenta de transformação para construir as tabelas de Process Intelligence. Assume-se que os dados brutos ou staging do Protheus **já estão no BigQuery**; o dbt atua a partir deles para produzir modelos intermediários (int) e marts (case_base, event_log).

- **BigQuery**: fonte e destino; queries e documentação via dbt.
- **dbt**: modelos em SQL, testes, documentação, linha de montagem clara (staging → int → mart).

## Consequências

- **Positivas**: Transformações versionadas, testes de qualidade (unique, not null, relationships), documentação gerada, alinhamento com prática comum de analytics; escalabilidade do BigQuery.
- **Negativas**: Equipe precisa conhecer dbt e SQL; custo de query no BigQuery deve ser monitorado.
- **Riscos**: Dados de origem fora do BigQuery exigiriam adaptadores ou ingestão prévia; assumido que o pipeline de ingestão é responsabilidade de outro sistema.

## Alternativas consideradas

1. **Apenas SQL/scripts no repositório**: Rejeitado por falta de testes estruturados e documentação automatizada.
2. **Spark/Databricks**: Rejeitado para o escopo inicial; BigQuery atende e reduz variedade de tecnologias.
3. **Ferramentas low-code (ex.: Dataform apenas como UI)**: dbt em código permite revisão, CI e portabilidade; preferido para laboratório e produto.
