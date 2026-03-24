from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Sx3FieldMeta:
    tipo: str | None
    tamanho: str | None
    decimal: str | None
    titulo: str | None
    desc: str | None
    desc_eng: str | None
    relacao: str | None
    f3: str | None
    trigger: str | None


def _norm_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v)
    s = s.strip()
    # SX3 costuma vir com strings vazias como " " ou repetições de espaços.
    if s == "" or s.lower() == "nan" or s.lower() == "none":
        return None
    return s


def _looks_like_table_code(s: str) -> bool:
    """
    Heurística: códigos de tabelas no Protheus costumam ser 2-4 caracteres
    (ex.: SE2, FK7, SB1, SA6, CTT).
    """
    return bool(re.fullmatch(r"[A-Z0-9]{2,4}", s))


def load_sx3_csv(path: Path | str) -> pd.DataFrame:
    """Carrega o SX3 CSV com normalização leve (trim) e dtype-safe."""
    df = pd.read_csv(path, low_memory=False)
    # Normaliza colunas-chave para reduzir discrepâncias de espaços.
    for c in ["X3_ARQUIVO", "X3_CAMPO", "X3_TITULO", "X3_DESCRIC", "X3_DESCSPA", "X3_DESCENG", "X3_F3", "X3_RELACAO", "X3_TRIGGER"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def build_sx3_metadata(df: pd.DataFrame) -> dict[str, dict[str, Sx3FieldMeta]]:
    """
    Retorna um índice: {table_code: {field_code: Sx3FieldMeta}}.
    """
    required = ["X3_ARQUIVO", "X3_CAMPO"]
    for r in required:
        if r not in df.columns:
            raise ValueError(f"SX3 CSV sem coluna obrigatória: {r}")

    meta: dict[str, dict[str, Sx3FieldMeta]] = {}

    # Colunas opcionais
    def g(col: str) -> str | None:
        return col  # marker

    for row in df.itertuples(index=False):
        table = _norm_str(getattr(row, "X3_ARQUIVO"))
        field = _norm_str(getattr(row, "X3_CAMPO"))
        if not table or not field:
            continue

        # Normaliza campo e tabela para maiúsculo padrão do Protheus.
        table = table.upper()
        field = field.upper()

        relacao = _norm_str(getattr(row, "X3_RELACAO", None))
        f3 = _norm_str(getattr(row, "X3_F3", None))
        trigger = _norm_str(getattr(row, "X3_TRIGGER", None))

        meta.setdefault(table, {})
        meta[table][field] = Sx3FieldMeta(
            tipo=_norm_str(getattr(row, "X3_TIPO", None)),
            tamanho=_norm_str(getattr(row, "X3_TAMANHO", None)),
            decimal=_norm_str(getattr(row, "X3_DECIMAL", None)),
            titulo=_norm_str(getattr(row, "X3_TITULO", None)),
            desc=_norm_str(getattr(row, "X3_DESCRIC", None)),
            desc_eng=_norm_str(getattr(row, "X3_DESCENG", None)),
            relacao=relacao,
            f3=f3 if (f3 and _looks_like_table_code(f3)) else f3,  # guarda mesmo se não for código
            trigger=trigger,
        )
    return meta

