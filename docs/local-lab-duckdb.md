# Laboratório local — BigQuery, Parquet e DuckDB

Objetivo do fluxo local: validar joins, case base, event log e regras semânticas **sem escrever no dataset oficial do BigQuery**. Tudo roda no seu ambiente com cópia controlada dos dados.

## Objetivo

- **Extrair** subconjuntos das tabelas do BigQuery (SE2, FK7, FK2, SE5) para arquivos Parquet locais.
- **Carregar** esses Parquets em um banco DuckDB local (`local/process_intelligence.duckdb`).
- **Materializar** localmente as tabelas `cp_case_base` e `cp_event_log` com SQL que segue o [contrato canônico](contracts/contas_a_pagar_process_intelligence.md) (1 caso = 1 título SE2, chave de 7 campos com TRIM, valor observado vs inferido, atividades padronizadas).
- Permitir testes e ajustes de lógica sem impactar o dbt/BigQuery de produção.

## Fluxo

```
BigQuery (fonte)  →  Parquet (data/extracts/)  →  DuckDB (local/)  →  marts (cp_case_base, cp_event_log)
                         ↑                              ↑
                    extract_bigquery_to_parquet    load_parquet_to_duckdb
                                                         ↑
                                              materialize_cp_case_base
                                              materialize_cp_event_log
```

## Como rodar

1. **Configuração**  
   Guia completo: [config-lab.md](config-lab.md). Resumo:
   - Copie `.env.example` para `.env`.
   - Preencha `BQ_PROJECT_ID` e `BQ_DATASET_RAW`.
   - Credenciais GCP: `gcloud auth application-default login` ou `GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/sa.json`.

2. **Orquestrador (recomendado)**
   ```bash
   ./scripts/run_local_lab.sh
   ```
   Executa em sequência: extração → carga DuckDB → materialização cp_case_base → materialização cp_event_log.

3. **Passo a passo**
   ```bash
   python -m python.local_lab.extract_bigquery_to_parquet
   python -m python.local_lab.load_parquet_to_duckdb
   python -m python.local_lab.materialize_cp_case_base
   python -m python.local_lab.materialize_cp_event_log
   ```

4. **Consultar o DuckDB**
   ```bash
   duckdb local/process_intelligence.duckdb
   ```
   Ex.: `SELECT * FROM cp_case_base LIMIT 10;`, `SELECT * FROM cp_event_log LIMIT 10;`

5. **Relatório schema Parquet vs SQL** (identificar divergências entre schema observado e hipóteses dos SQLs):
   ```bash
   python scripts/report_parquet_schema_vs_sql.py -o docs/schema-parquet-vs-sql-report.md
   ```
   Ver `docs/schema-parquet-vs-sql-report.md`.

## Estrutura criada

| Caminho | Papel |
|--------|--------|
| `data/extracts/*.parquet` | Cópias locais das tabelas BQ (se2, fk7, fk2, se5). |
| `data/marts/*.parquet` | Export opcional dos marts (cp_case_base, cp_event_log). |
| `local/process_intelligence.duckdb` | Banco DuckDB com stg_* e marts. |
| `sql/marts/cp_case_base.sql` | SQL do case base (DuckDB). |
| `sql/marts/cp_event_log.sql` | SQL do event log (DuckDB). |
| `python/local_lab/*.py` | Scripts de extração, carga e materialização. |

## Por que não poluir o BigQuery

- Nenhuma tabela é criada no dataset de analytics/produção.
- A extração é **leitura** no BQ (SELECT com LIMIT/filtro opcional).
- Joins e regras são testados no DuckDB e em Parquet; quando estiverem estáveis, a mesma lógica pode ser refletida no dbt para o BQ.

## Lógica validada empiricamente (dados Protheus no DuckDB)

- **SE2 (saldo + baixa)** é a verdade operacional do encerramento: `e2_saldo = 0` e `e2_baixa IS NOT NULL` indicam título baixado.
- **SE5** é evidência bancária (pagamento observado), não a única verdade de pagamento; existe volume relevante de **PAGO_SEM_SE5** (baixa sem SE5).
- **e2_status** não é confiável neste ambiente (quase todo vazio); a classificação de status não usa mais esse campo.
- **e2_datalib** é usado para o evento `TITULO_LIBERADO`; **e2_baixa** para data fim e evento `BAIXA_SEM_SE5` quando não há SE5.
- **Cancelamento** não implementado: `e2_datacan` e `e2_usuacan` vazios nos dados validados.

## O que ainda depende de validação

- **Nomes reais de colunas** no BigQuery (E2_FILIAL, E2_PREFIXO, … ou variantes). O extract normaliza para minúsculo (e2_filial, etc.); o SQL local assume esses nomes. Se o schema real for outro, ajuste as queries no extract ou no SQL.
- **Nomes das tabelas** no dataset (ex.: `se2` vs `SE2`). Configure `BQ_TABLE_SE2`, etc., no `.env`.
- **Tipos e datas**: se houver data/hora em colunas separadas, a lógica de `event_timestamp_original` pode precisar de ajuste (hoje usa strptime para campos numéricos YYYYMMDD onde aplicável).

O contrato em `docs/contracts/contas_a_pagar_process_intelligence.md` define o **que** deve ser entregue (caso, chave, TRIM); o laboratório local implementa o **como** de forma que possa evoluir conforme o schema real for validado.

## Próximos passos (após rodar o lab)

| Ação | Comando / Onde | Objetivo |
|------|----------------|----------|
| **Relatório schema** | `uv run python scripts/report_parquet_schema_vs_sql.py -o docs/schema-parquet-vs-sql-report.md` | Comparar colunas dos Parquets com as usadas nos SQLs; ver divergências. |
| **Explorar no DuckDB** | `duckdb local/process_intelligence.duckdb` | Consultar `cp_case_base`, `cp_event_log` (ex.: status_macro, atividades, duração). |
| **Validar contrato** | `uv run python scripts/validate_contract_alignment.py` | Verificar aderência ao contrato (exige `dbt/models/` com marts; opcional para lab local). |
| **Process mining** | Implementar em `python/mining/` (discovery, variants, bottlenecks) | Ler `data/marts/cp_event_log.parquet` com PM4Py; descoberta de processo, variantes, gargalos. |
| **Subir para dbt/BigQuery** | Replicar lógica de `sql/marts/*.sql` em modelos dbt | Quando a lógica estiver validada no lab, materializar marts no dataset de analytics. |
