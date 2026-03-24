#!/usr/bin/env python3
"""
Investiga fluxos alternativos de pagamento para casos PAGO_SEM_SE5.

Usa DuckDB local (cp_case_base, stg_*) e, se existirem, Parquets de FK1/FK5/FK6.
Gera relatório em docs/investigacao-fluxos-pago-sem-se5.md.

Uso: uv run python scripts/investigate_pago_sem_se5_flows.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.local_lab import config


def _path(p: Path) -> str:
    return p.resolve().as_posix()


def run(conn, sql: str):
    return conn.execute(sql).fetchall()


def run_one(conn, sql: str):
    row = conn.execute(sql).fetchone()
    return row[0] if row else None


def main() -> int:
    try:
        import duckdb
    except ImportError:
        print("ERRO: duckdb não instalado.")
        return 1

    out_lines: list[str] = []

    # Prefer existing DuckDB; if locked or missing, use in-memory DB loaded from parquets
    conn = None
    use_memory = not config.DUCKDB_PATH.exists()
    if config.DUCKDB_PATH.exists():
        try:
            conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
        except Exception:
            use_memory = True

    if use_memory:
        conn = duckdb.connect(":memory:")
        extracts = config.EXTRACTS_DIR
        marts = config.MARTS_DIR
        for name, path in [
            ("stg_se2", extracts / "se2.parquet"),
            ("stg_fk7", extracts / "fk7.parquet"),
            ("stg_fk2", extracts / "fk2.parquet"),
            ("stg_se5", extracts / "se5.parquet"),
            ("cp_case_base", marts / "cp_case_base.parquet"),
        ]:
            if path.exists():
                conn.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_parquet('{_path(path)}')")
        if not (marts / "cp_case_base.parquet").exists():
            print("ERRO: cp_case_base.parquet não encontrado. Rode o laboratório local antes.")
            return 1
        print("(Usando cópia em memória a partir dos Parquets; DuckDB em disco indisponível ou em uso.)")
    append = out_lines.append

    append("# Investigação: fluxos alternativos de pagamento (PAGO_SEM_SE5)")
    append("")
    append("Relatório gerado por `scripts/investigate_pago_sem_se5_flows.py`.")
    append("Casos-alvo: `cp_case_base` onde `status_macro = 'PAGO_SEM_SE5'`.")
    append("")
    append("---")
    append("")

    # Total PAGO_SEM_SE5
    n_pago_sem_se5 = run_one(conn, "SELECT COUNT(*) FROM cp_case_base WHERE status_macro = 'PAGO_SEM_SE5'")
    n_total_cb = run_one(conn, "SELECT COUNT(*) FROM cp_case_base")
    append("## Resumo dos casos PAGO_SEM_SE5")
    append("")
    append(f"- Total de casos no case_base: **{n_total_cb}**")
    append(f"- Casos PAGO_SEM_SE5: **{n_pago_sem_se5}**")
    if n_total_cb and n_total_cb > 0:
        pct = round(100 * n_pago_sem_se5 / n_total_cb, 1)
        append(f"- Percentual: **{pct}%**")
    append("")

    # 1) SE5 e E5_IDORIG
    append("## 1. SE5 — E5_IDORIG vazio/nulo e ligação por chave")
    append("")
    cols = [r[0] for r in run(conn, "DESCRIBE SELECT * FROM stg_se5")]
    has_idorig = any(c.upper() == "E5_IDORIG" or c.lower() == "e5_idorig" for c in cols)
    if has_idorig:
        col_idorig = "e5_idorig" if "e5_idorig" in [c.lower() for c in cols] else "E5_IDORIG"
        n_se5 = run_one(conn, "SELECT COUNT(*) FROM stg_se5")
        n_idorig_null = run_one(conn, f"SELECT COUNT(*) FROM stg_se5 WHERE {col_idorig} IS NULL OR TRIM(CAST({col_idorig} AS VARCHAR)) = ''")
        append(f"- Total de registros SE5: **{n_se5}**")
        append(f"- Registros com E5_IDORIG vazio ou nulo: **{n_idorig_null}**")
        if n_se5 and n_se5 > 0:
            append(f"- Percentual sem IDORIG: **{round(100 * n_idorig_null / n_se5, 1)}%**")
    else:
        append("- Coluna **E5_IDORIG** não encontrada em `stg_se5`. Colunas disponíveis (amostra): " + ", ".join(cols[:20]))
    append("")
    append("Chave candidata SE5 ↔ título (7 campos): filial, prefixo, número, parcela, tipo, fornecedor/clifor, loja.")
    append("")
    append("Amostra SE5 (20 registros):")
    append("")
    try:
        sample = run(conn, "SELECT * FROM stg_se5 LIMIT 20")
        if sample:
            headers = [d[0] for d in conn.execute("DESCRIBE SELECT * FROM stg_se5").fetchall()]
            append("| " + " | ".join(str(h) for h in headers[:12]) + " |")
            append("|" + " --- |" * min(12, len(headers)))
            for row in sample:
                append("| " + " | ".join(str(v)[:30] for v in row[:12]) + " |")
        else:
            append("(nenhum registro)")
    except Exception as e:
        append(f"(erro ao amostrar: {e})")
    append("")

    # 2) FK1 — borderô
    append("## 2. FK1 — cobertura para PAGO_SEM_SE5 (borderô)")
    append("")
    fk1_path = config.PARQUET_FK1
    if not fk1_path.exists():
        append("- **Arquivo FK1 não encontrado:** `" + str(fk1_path) + "`")
        append("- Para incluir: rode a extração BigQuery → Parquet (FK1 já configurado no lab).")
    else:
        path_str = _path(fk1_path)
        n_fk1 = run_one(conn, f"SELECT COUNT(*) FROM read_parquet('{path_str}')")
        append(f"- Total de registros FK1: **{n_fk1}**")
        # Chaves candidatas
        try:
            fk1_cols = [r[0] for r in conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{path_str}')").fetchall()]
            append("- Colunas (chaves candidatas para SE2): " + ", ".join(fk1_cols[:25]))
            # Cobertura: precisamos de case_id no mesmo formato. FK1 pode ter FK1_IDDOC e ligar via FK7.
            # Criar view temporária com case_id a partir de FK7 se tivermos FK1_IDDOC
            if "FK1_IDDOC" in fk1_cols or "fk1_iddoc" in [c.lower() for c in fk1_cols]:
                iddoc_col = "FK1_IDDOC" if "FK1_IDDOC" in fk1_cols else "fk1_iddoc"
                try:
                    n_intersect = run_one(conn, f"""
                        SELECT COUNT(DISTINCT p.case_id)
                        FROM (SELECT case_id FROM cp_case_base WHERE status_macro = 'PAGO_SEM_SE5') p
                        INNER JOIN (
                            SELECT DISTINCT
                                COALESCE(TRIM(CAST(f.FK7_FILIAL AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_PREFIX AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_NUM AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_PARCEL AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_TIPO AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_CLIFOR AS VARCHAR)), '') || '|' ||
                                COALESCE(TRIM(CAST(f.FK7_LOJA AS VARCHAR)), '') AS case_id
                            FROM read_parquet('{path_str}') f1
                            JOIN stg_fk7 f ON f1."{iddoc_col}" = f."FK7_IDDOC"
                        ) f ON p.case_id = f.case_id
                    """)
                    append(f"- Casos PAGO_SEM_SE5 que aparecem em FK1 (via FK7_IDDOC): **{n_intersect}**")
                    if n_pago_sem_se5 and n_pago_sem_se5 > 0:
                        append(f"- Percentual dos PAGO_SEM_SE5 com borderô (FK1): **{round(100 * n_intersect / n_pago_sem_se5, 1)}%**")
                except Exception as e2:
                    append(f"- Cobertura não calculada (ligação FK1↔case_id): {e2}")
            else:
                append("- Ligação com case_id não feita (FK1_IDDOC ou equivalente não encontrado).")
        except Exception as e:
            append(f"- Erro ao inspecionar FK1: {e}")
    append("")

    # 3) FK5 — remessa CNAB
    append("## 3. FK5 — cobertura para PAGO_SEM_SE5 (remessa CNAB)")
    append("")
    fk5_path = config.PARQUET_FK5
    if not fk5_path.exists():
        append("- **Arquivo FK5 não encontrado:** `" + str(fk5_path) + "`")
    else:
        path_str = _path(fk5_path)
        n_fk5 = run_one(conn, f"SELECT COUNT(*) FROM read_parquet('{path_str}')")
        append(f"- Total de registros FK5: **{n_fk5}**")
        try:
            fk5_cols = [r[0] for r in conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{path_str}')").fetchall()]
            append("- Colunas (amostra): " + ", ".join(fk5_cols[:25]))
            # Cobertura: FK5 pode ter FK5_IDDOC -> FK7 -> case_id
            iddoc = next((c for c in fk5_cols if "IDDOC" in c.upper() or "iddoc" in c.lower()), None)
            if iddoc:
                n_intersect5 = run_one(conn, f"""
                    SELECT COUNT(DISTINCT p.case_id)
                    FROM (SELECT case_id FROM cp_case_base WHERE status_macro = 'PAGO_SEM_SE5') p
                    INNER JOIN (
                        SELECT DISTINCT
                            COALESCE(TRIM(CAST(f.FK7_FILIAL AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_PREFIX AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_NUM AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_PARCEL AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_TIPO AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_CLIFOR AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_LOJA AS VARCHAR)), '') AS case_id
                        FROM read_parquet('{path_str}') f5
                        JOIN stg_fk7 f ON f5."{iddoc}" = f."FK7_IDDOC"
                    ) f ON p.case_id = f.case_id
                """)
                append(f"- Casos PAGO_SEM_SE5 com remessa CNAB (FK5): **{n_intersect5}**")
                if n_pago_sem_se5 and n_pago_sem_se5 > 0:
                    append(f"- Percentual: **{round(100 * n_intersect5 / n_pago_sem_se5, 1)}%**")
        except Exception as e:
            append(f"- Erro FK5: {e}")
    append("")

    # 4) FK6 — retorno bancário
    append("## 4. FK6 — cobertura para PAGO_SEM_SE5 (retorno bancário)")
    append("")
    fk6_path = config.PARQUET_FK6
    if not fk6_path.exists():
        append("- **Arquivo FK6 não encontrado:** `" + str(fk6_path) + "`")
    else:
        path_str = _path(fk6_path)
        n_fk6 = run_one(conn, f"SELECT COUNT(*) FROM read_parquet('{path_str}')")
        append(f"- Total de registros FK6: **{n_fk6}**")
        try:
            fk6_cols = [r[0] for r in conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{path_str}')").fetchall()]
            append("- Colunas (amostra): " + ", ".join(fk6_cols[:25]))
            data_cols = [c for c in fk6_cols if "DATA" in c.upper() or "DT" in c.upper() or "VENCTO" in c.upper() or "CONF" in c.upper()]
            if data_cols:
                append("- Campos de data/confirmação candidatos: " + ", ".join(data_cols))
            iddoc = next((c for c in fk6_cols if "IDDOC" in c.upper() or "iddoc" in c.lower()), None)
            if iddoc:
                n_intersect6 = run_one(conn, f"""
                    SELECT COUNT(DISTINCT p.case_id)
                    FROM (SELECT case_id FROM cp_case_base WHERE status_macro = 'PAGO_SEM_SE5') p
                    INNER JOIN (
                        SELECT DISTINCT
                            COALESCE(TRIM(CAST(f.FK7_FILIAL AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_PREFIX AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_NUM AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_PARCEL AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_TIPO AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_CLIFOR AS VARCHAR)), '') || '|' ||
                            COALESCE(TRIM(CAST(f.FK7_LOJA AS VARCHAR)), '') AS case_id
                        FROM read_parquet('{path_str}') f6
                        JOIN stg_fk7 f ON f6."{iddoc}" = f."FK7_IDDOC"
                    ) f ON p.case_id = f.case_id
                """)
                append(f"- Casos PAGO_SEM_SE5 com retorno bancário (FK6): **{n_intersect6}**")
                if n_pago_sem_se5 and n_pago_sem_se5 > 0:
                    append(f"- Percentual: **{round(100 * n_intersect6 / n_pago_sem_se5, 1)}%**")
        except Exception as e:
            append(f"- Erro FK6: {e}")
    append("")

    # 5) Amostras FK1/FK5/FK6 (20 registros cada)
    for name, path in [
        ("FK1", config.PARQUET_FK1),
        ("FK5", config.PARQUET_FK5),
        ("FK6", config.PARQUET_FK6),
    ]:
        append(f"## Amostra {name} (20 registros)")
        append("")
        if not path.exists():
            append(f"- Arquivo não encontrado: `{path}`")
        else:
            try:
                path_str = _path(path)
                sample = run(conn, f"SELECT * FROM read_parquet('{path_str}') LIMIT 20")
                if sample:
                    headers = [d[0] for d in conn.execute(f"DESCRIBE SELECT * FROM read_parquet('{path_str}')").fetchall()]
                    append("| " + " | ".join(str(h) for h in headers[:10]) + " |")
                    append("|" + " --- |" * min(10, len(headers)))
                    for row in sample:
                        append("| " + " | ".join(str(v)[:25] for v in row[:10]) + " |")
                else:
                    append("(vazio)")
            except Exception as e:
                append(f"(erro: {e})")
        append("")

    # 6) Conclusões
    append("---")
    append("## Conclusões e recomendações")
    append("")
    append("- **Fluxos alternativos confirmados:** (preencher após análise dos resultados acima).")
    append("- **Tabelas que ajudam a fechar o processo:** (FK1 borderô, FK5 remessa, FK6 retorno — conforme cobertura).")
    append("- **Novos eventos sugeridos para o event_log:** (ex.: BORDERÓ_GERADO, REMESSA_CNAB, RETORNO_BANCÁRIO — somente se evidência for alta).")
    append("- **Hipóteses refutadas:** (listar se alguma expectativa não se confirmou).")
    append("")
    append("*Este relatório é apenas evidência; não altera marts até decisão de modelagem.*")

    conn.close()

    out_path = REPO_ROOT / "docs" / "investigacao-fluxos-pago-sem-se5.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Relatório gerado: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
