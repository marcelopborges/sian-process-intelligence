#!/usr/bin/env python3
"""
Valida cp_event_log_semantic: top variantes, ancoragem em TITULO_CRIADO,
distribuição por activity, eventos por caso.

Uso: python scripts/validate_cp_event_log_semantic.py

Requisitos: DuckDB com cp_event_log (e opcionalmente cp_event_log_semantic
já materializado). Se a tabela não existir, usa a lógica do SQL semantic
inline para rodar as validações.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python.local_lab import config


def main() -> None:
    try:
        import duckdb
    except ImportError:
        print("ERRO: duckdb não instalado.")
        sys.exit(1)

    if not config.DUCKDB_PATH.exists():
        print(f"ERRO: DuckDB não encontrado: {config.DUCKDB_PATH}")
        sys.exit(1)

    # Tentar read_only primeiro para não bloquear se outro processo estiver escrevendo
    try:
        conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=True)
    except Exception:
        conn = duckdb.connect(str(config.DUCKDB_PATH), read_only=False)

    # Usar tabela materializada cp_event_log_semantic quando existir
    table_exists = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'cp_event_log_semantic'"
    ).fetchone()[0] > 0

    print("=== Validações cp_event_log_semantic ===\n")

    if not table_exists:
        print("AVISO: Tabela cp_event_log_semantic não existe. Rode antes: python -m python.local_lab.materialize_cp_event_log_semantic")
        conn.close()
        sys.exit(1)

    # A. Top 10 variantes
    print("--- A. Top 10 variantes ---")
    q_a = """
    WITH paths_por_caso AS (
      SELECT
        case_id,
        STRING_AGG(activity, ' → ' ORDER BY event_order_semantic, event_timestamp_semantic) AS path
      FROM cp_event_log_semantic
      GROUP BY case_id
    )
    SELECT path, COUNT(*) AS qtd_cases
    FROM paths_por_caso
    GROUP BY path
    ORDER BY qtd_cases DESC
    LIMIT 10
    """
    rows = conn.execute(q_a).fetchall()
    for path, qtd in rows:
        print(f"  {qtd:>8}  {path}")
    print()

    # B. Nenhuma variante deve começar sem TITULO_CRIADO
    print("--- B. Verificação: nenhuma variante começa sem TITULO_CRIADO ---")
    q_b = """
    WITH first_activity AS (
      SELECT case_id,
             FIRST(activity ORDER BY event_order_semantic, event_timestamp_semantic) AS first_act
      FROM cp_event_log_semantic
      GROUP BY case_id
    )
    SELECT COUNT(*) AS invalidos FROM first_activity WHERE first_act != 'TITULO_CRIADO'
    """
    (invalidos,) = conn.execute(q_b).fetchone()
    if invalidos == 0:
        print("  OK: Todas as variantes começam com TITULO_CRIADO.")
    else:
        print(f"  ERRO: {invalidos} caso(s) não começam com TITULO_CRIADO.")
    print()

    # C. Distribuição por activity
    print("--- C. Distribuição por activity ---")
    q_c = """
    SELECT activity, COUNT(*)
    FROM cp_event_log_semantic
    GROUP BY 1
    ORDER BY 2 DESC
    """
    rows = conn.execute(q_c).fetchall()
    for act, cnt in rows:
        print(f"  {act:<35}  {cnt:>10}")
    print()

    # D. Eventos por caso (média, min, max)
    print("--- D. Eventos por caso ---")
    q_d = """
    WITH por_caso AS (SELECT case_id, COUNT(*) AS cnt FROM cp_event_log_semantic GROUP BY case_id)
    SELECT AVG(cnt) AS media_eventos, MIN(cnt) AS min_eventos, MAX(cnt) AS max_eventos
    FROM por_caso
    """
    row = conn.execute(q_d).fetchone()
    print(f"  Média: {row[0]:.2f}  |  Mín: {row[1]}  |  Máx: {row[2]}")

    conn.close()
    print("\nConcluído.")


if __name__ == "__main__":
    main()
