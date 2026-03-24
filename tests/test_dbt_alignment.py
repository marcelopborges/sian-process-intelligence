from __future__ import annotations

from app.validation.dbt_alignment import classify_event_candidate, load_mart_registry


def test_alinhado_mart_se2_emissao():
    mart = load_mart_registry(domain="cp")
    duck = {"SE2": {"E2_EMISSAO", "E2_DBALTERACAO", "E2_VENCIMENTO"}}
    cls, _, level = classify_event_candidate(
        activity="TITULO_CRIADO",
        source_table="SE2",
        source_column="E2_EMISSAO",
        duckdb_columns_by_table=duck,
        mart=mart,
    )
    assert cls == "ALINHADO_MART"
    assert level == "ALTA"


def test_sem_coluna_na_fonte():
    mart = load_mart_registry(domain="cp")
    duck = {"SE2": {"E2_EMISSAO"}}
    cls, _, _ = classify_event_candidate(
        activity="TITULO_CRIADO",
        source_table="SE2",
        source_column="E2_INEXISTENTE",
        duckdb_columns_by_table=duck,
        mart=mart,
    )
    assert cls == "SEM_COLUNA_NA_FONTE"


def test_requer_validacao_negocio_fk7():
    mart = load_mart_registry(domain="cp")
    duck = {"FK7": {"F7_DATA_EVENTO", "F7_COD_EVENTO"}}
    cls, _, _ = classify_event_candidate(
        activity="TITULO_CRIADO",
        source_table="FK7",
        source_column="F7_DATA_EVENTO",
        duckdb_columns_by_table=duck,
        mart=mart,
    )
    assert cls == "REQUER_VALIDACAO_NEGOCIO"
