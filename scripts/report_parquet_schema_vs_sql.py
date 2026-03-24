#!/usr/bin/env python3
"""
Gera relatório técnico: colunas/tipos/amostras dos Parquets extraídos
vs colunas assumidas nos SQLs cp_case_base.sql e cp_event_log.sql.

Uso: python scripts/report_parquet_schema_vs_sql.py [--output ARQUIVO]

Saída: Markdown com schema observado, amostras, hipóteses dos SQLs e divergências.
Se os Parquets não existirem, o relatório ainda lista as hipóteses e indica "dados não disponíveis".
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTRACTS_DIR = REPO_ROOT / "data" / "extracts"
SQL_CASE_BASE = REPO_ROOT / "sql" / "marts" / "cp_case_base.sql"
SQL_EVENT_LOG = REPO_ROOT / "sql" / "marts" / "cp_event_log.sql"

# Colunas assumidas nos SQLs (extraídas da análise estática dos arquivos)
ASSUMED_COLUMNS = {
    "stg_se2": [
        "e2_filial", "e2_prefixo", "e2_num", "e2_parcela", "e2_tipo", "e2_fornece", "e2_loja",
        "e2_valor", "e2_moeda", "e2_emissao", "e2_vencimento", "e2_status", "e2_dbalteracao",
    ],
    "stg_fk7": [
        "f7_filial", "f7_prefixo", "f7_num", "f7_parcela", "f7_tipo", "f7_fornece", "f7_loja",
        "f7_cod_evento", "f7_data_evento", "f7_dbalteracao", "f7_usuario", "f7_hora_evento",
    ],
    "stg_fk2": [
        "f2_filial", "f2_prefixo", "f2_num", "f2_parcela", "f2_tipo", "f2_fornece", "f2_loja",
        "f2_data_lancamento", "f2_hora_lancamento", "f2_dbalteracao",
    ],
    "stg_se5": [
        "e5_filial", "e5_prefixo", "e5_num", "e5_parcela", "e5_tipo", "e5_fornece", "e5_loja",
        "e5_data_pagamento", "e5_valor_pago", "e5_hora_pagamento", "e5_usuario",
    ],
}

PARQUET_FILES = {
    "stg_se2": EXTRACTS_DIR / "se2.parquet",
    "stg_fk7": EXTRACTS_DIR / "fk7.parquet",
    "stg_fk2": EXTRACTS_DIR / "fk2.parquet",
    "stg_se5": EXTRACTS_DIR / "se5.parquet",
}


def read_parquet_schema_and_sample(path: Path) -> tuple[list[str], dict[str, str], int, object] | None:
    """Retorna (colunas, {col: dtype}, n_rows, df_head) ou None se falhar."""
    try:
        import pandas as pd
    except ImportError:
        return None
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
    except Exception:
        return None
    cols = list(df.columns)
    dtypes = {c: str(df.dtypes[c]) for c in cols}
    n = len(df)
    head = df.head(5) if n > 0 else None
    return (cols, dtypes, n, head)


def extract_column_refs_from_sql(sql_path: Path) -> set[str]:
    """Extrai referências a colunas no formato prefixo_nome (ex: e2_filial, f7_cod_evento)."""
    if not sql_path.exists():
        return set()
    text = sql_path.read_text(encoding="utf-8")
    # Padrão: palavra que contém número + underscore (e2_filial, f7_xxx, e5_xxx, f2_xxx)
    refs = set()
    for m in re.finditer(r"\b(e2_|f7_|f2_|e5_)\w+", text, re.IGNORECASE):
        refs.add(m.group(0).lower())
    return refs


def main() -> None:
    parser = argparse.ArgumentParser(description="Relatório Parquet vs SQL (schema e amostras)")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Arquivo de saída Markdown (default: stdout)")
    args = parser.parse_args()
    out_path = args.output

    lines = []
    def w(s: str = "") -> None:
        lines.append(s)

    w("# Relatório técnico: schema Parquet vs hipóteses dos SQLs")
    w()
    w("Comparação entre as colunas/tipos/amostras dos arquivos Parquet em `data/extracts/` e as colunas utilizadas em `sql/marts/cp_case_base.sql` e `sql/marts/cp_event_log.sql`.")
    w()
    w("---")
    w()

    observed = {}
    for table, parquet_path in PARQUET_FILES.items():
        result = read_parquet_schema_and_sample(parquet_path)
        if result is None:
            observed[table] = None
            continue
        cols, dtypes, n, head = result
        observed[table] = {"columns": cols, "dtypes": dtypes, "n_rows": n, "head": head}

    # Referências extras nos SQLs (para comparação)
    refs_case = extract_column_refs_from_sql(SQL_CASE_BASE)
    refs_event = extract_column_refs_from_sql(SQL_EVENT_LOG)
    all_sql_refs = refs_case | refs_event

    for table in ("stg_se2", "stg_fk7", "stg_fk2", "stg_se5"):
        w(f"## {table}")
        w()
        assumed = set(ASSUMED_COLUMNS.get(table, []))
        obs = observed.get(table)
        if obs is None:
            w("**Dados:** Parquet não encontrado ou não legível.")
            w()
            w("**Colunas assumidas nos SQLs:**")
            for c in sorted(assumed):
                w(f"- `{c}`")
            w()
            w("---")
            w()
            continue

        cols_obs = obs["columns"]
        dtypes_obs = obs["dtypes"]
        n_rows = obs["n_rows"]
        head = obs["head"]

        w(f"**Arquivo:** `{PARQUET_FILES[table]}`  ")
        w(f"**Linhas:** {n_rows}")
        w()
        w("### Colunas observadas (ordem e tipo)")
        w()
        w("| Coluna | Tipo (pandas) |")
        w("|--------|----------------|")
        for c in cols_obs:
            w(f"| `{c}` | `{dtypes_obs.get(c, '')}` |")
        w()
        w("### Amostra de valores (até 5 linhas)")
        w()
        if head is not None and len(head) > 0:
            # Markdown table: colunas como cabeçalho, linhas truncadas
            sample_df = head
            cols_display = list(sample_df.columns)[:12]  # limitar colunas para não estourar
            sample_df = sample_df[cols_display]
            w("| " + " | ".join(f"`{c}`" for c in sample_df.columns) + " |")
            w("| " + " | ".join("---" for _ in sample_df.columns) + " |")
            for _, row in sample_df.iterrows():
                cells = []
                for v in row:
                    s = str(v)
                    if len(s) > 30:
                        s = s[:27] + "..."
                    cells.append(s.replace("|", "\\|"))
                w("| " + " | ".join(cells) + " |")
        else:
            w("*Sem linhas.*")
        w()
        w("### Comparação com as hipóteses dos SQLs")
        w()
        cols_obs_set = {c.lower() for c in cols_obs}
        assumed_lower = {c.lower() for c in assumed}
        missing_in_parquet = assumed_lower - cols_obs_set
        extra_in_parquet = cols_obs_set - assumed_lower
        if not missing_in_parquet and not extra_in_parquet:
            w("- **Aderência:** Todas as colunas assumidas existem no Parquet; não há colunas extras referenciadas nos SQLs.")
        else:
            if missing_in_parquet:
                w("- **Colunas usadas no SQL mas ausentes no Parquet:**")
                for c in sorted(missing_in_parquet):
                    w(f"  - `{c}` → **divergência**")
            if extra_in_parquet:
                w("- **Colunas no Parquet não referenciadas nos SQLs atuais:**")
                for c in sorted(extra_in_parquet):
                    w(f"  - `{c}`")
        w()
        w("---")
        w()

    w("## Resumo de divergências")
    w()
    divergences = []
    for table in ("stg_se2", "stg_fk7", "stg_fk2", "stg_se5"):
        obs = observed.get(table)
        if obs is None:
            divergences.append(f"- **{table}**: sem Parquet; não é possível comparar.")
            continue
        assumed = {c.lower() for c in ASSUMED_COLUMNS.get(table, [])}
        cols_obs_set = {c.lower() for c in obs["columns"]}
        missing = assumed - cols_obs_set
        if missing:
            divergences.append(f"- **{table}**: colunas assumidas ausentes no Parquet: {', '.join(sorted(missing))}")
    if not divergences:
        divergences.append("- Nenhuma divergência crítica detectada (colunas assumidas presentes nos Parquets).")
    for d in divergences:
        w(d)
    w()
    w("---")
    w()
    w("*Relatório gerado por `scripts/report_parquet_schema_vs_sql.py`. Execute após extrair Parquets com `python -m app.lab.extract_bigquery_to_parquet`.*")

    report = "\n".join(lines)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Relatório gravado em: {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
