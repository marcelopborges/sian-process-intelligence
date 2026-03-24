from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.discovery.sx3_loader import build_sx3_metadata


def test_sx3_loader_builds_meta_for_known_table_and_field():
    sx3_csv = Path("data/others/SX3010_202603231122.csv")
    assert sx3_csv.exists()

    # Arquivo grande: carregamos apenas colunas usadas pelo build_sx3_metadata.
    usecols = [
        "X3_ARQUIVO",
        "X3_CAMPO",
        "X3_TIPO",
        "X3_TAMANHO",
        "X3_DECIMAL",
        "X3_TITULO",
        "X3_DESCRIC",
        "X3_DESCENG",
        "X3_F3",
        "X3_RELACAO",
        "X3_TRIGGER",
    ]
    df = pd.read_csv(sx3_csv, low_memory=False, usecols=usecols)
    assert "X3_ARQUIVO" in df.columns
    assert "X3_CAMPO" in df.columns

    meta = build_sx3_metadata(df)
    # O SX3 deve conter ao menos SE2 e campos como E2_PREFIXO/E2_PARCELA em geral.
    assert "SE2" in meta
    assert "E2_PREFIXO" in meta["SE2"]

