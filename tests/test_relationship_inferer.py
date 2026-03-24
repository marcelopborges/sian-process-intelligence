from __future__ import annotations

from app.discovery.relationship_inferer import _token_from_column, infer_relationship_suggestions
from app.discovery.sx3_loader import Sx3FieldMeta


def test_token_from_column_extracts_suffix_token():
    assert _token_from_column("FK7_PREFIX") == "PREFIX"
    assert _token_from_column("e2_prefixo") == "PREFIX"
    assert _token_from_column("SE2") is None


def test_infer_relationship_suggestions_minimal_case():
    sx3_meta = {
        "SE2": {
            "E2_PREFIXO": Sx3FieldMeta(
                tipo="C",
                tamanho=None,
                decimal=None,
                titulo="Prefixo",
                desc="Prefixo do Titulo",
                desc_eng=None,
                relacao=None,
                f3=None,
                trigger=None,
            )
        },
        "FK7": {
            "FK7_PREFIX": Sx3FieldMeta(
                tipo="C",
                tamanho=None,
                decimal=None,
                titulo="Prefixo",
                desc="Prefixo do título",
                desc_eng=None,
                relacao=None,
                f3=None,
                trigger=None,
            )
        },
    }

    duckdb_tables = [
        ("stg_se2", ["e2_prefixo"]),
        ("stg_fk7", ["FK7_PREFIX"]),
    ]

    suggestions = infer_relationship_suggestions(sx3_meta=sx3_meta, duckdb_tables=duckdb_tables)
    assert len(suggestions) >= 1
    s = suggestions[0]
    assert s.source_table in {"SE2", "FK7"}
    assert s.target_table in {"SE2", "FK7"}
    assert "token_match" in s.reason

