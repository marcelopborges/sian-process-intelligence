# Relatório técnico: schema Parquet vs hipóteses dos SQLs

Comparação entre as colunas/tipos/amostras dos arquivos Parquet em `data/extracts/` e as colunas utilizadas em `sql/marts/cp_case_base.sql` e `sql/marts/cp_event_log.sql`.

---

## stg_se2

**Dados:** Parquet não encontrado ou não legível.

**Colunas assumidas nos SQLs:**
- `e2_dbalteracao`
- `e2_emissao`
- `e2_filial`
- `e2_fornece`
- `e2_loja`
- `e2_moeda`
- `e2_num`
- `e2_parcela`
- `e2_prefixo`
- `e2_status`
- `e2_tipo`
- `e2_valor`
- `e2_vencimento`

---

## stg_fk7

**Dados:** Parquet não encontrado ou não legível.

**Colunas assumidas nos SQLs:**
- `f7_cod_evento`
- `f7_data_evento`
- `f7_dbalteracao`
- `f7_filial`
- `f7_fornece`
- `f7_hora_evento`
- `f7_loja`
- `f7_num`
- `f7_parcela`
- `f7_prefixo`
- `f7_tipo`
- `f7_usuario`

---

## stg_fk2

**Dados:** Parquet não encontrado ou não legível.

**Colunas assumidas nos SQLs:**
- `f2_data_lancamento`
- `f2_dbalteracao`
- `f2_filial`
- `f2_fornece`
- `f2_hora_lancamento`
- `f2_loja`
- `f2_num`
- `f2_parcela`
- `f2_prefixo`
- `f2_tipo`

---

## stg_se5

**Dados:** Parquet não encontrado ou não legível.

**Colunas assumidas nos SQLs:**
- `e5_data_pagamento`
- `e5_filial`
- `e5_fornece`
- `e5_hora_pagamento`
- `e5_loja`
- `e5_num`
- `e5_parcela`
- `e5_prefixo`
- `e5_tipo`
- `e5_usuario`
- `e5_valor_pago`

---

## Resumo de divergências

- **stg_se2**: sem Parquet; não é possível comparar.
- **stg_fk7**: sem Parquet; não é possível comparar.
- **stg_fk2**: sem Parquet; não é possível comparar.
- **stg_se5**: sem Parquet; não é possível comparar.

---

*Relatório gerado por `scripts/report_parquet_schema_vs_sql.py`. Execute após extrair Parquets com `python -m python.local_lab.extract_bigquery_to_parquet`.*