#!/usr/bin/env bash
# =============================================================================
# Laboratório local: BigQuery -> Parquet -> DuckDB -> cp_case_base + cp_event_log
# =============================================================================
# Uso: ./scripts/run_local_lab.sh
# Requisitos: uv (https://github.com/astral-sh/uv), .env opcional
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

echo "=== Laboratório local Process Intelligence ==="
echo ""

echo "[1/4] Extração BigQuery -> Parquet"
uv run python -m python.local_lab.extract_bigquery_to_parquet || {
  echo "AVISO: Extração falhou (credenciais BQ?). Crie data/extracts/*.parquet manualmente para continuar."
  exit 1
}

echo ""
echo "[2/4] Carga Parquet -> DuckDB"
uv run python -m python.local_lab.load_parquet_to_duckdb

echo ""
echo "[3/4] Materialização cp_case_base"
uv run python -m python.local_lab.materialize_cp_case_base

echo ""
echo "[4/5] Materialização cp_event_log"
uv run python -m python.local_lab.materialize_cp_event_log

echo ""
echo "[5/5] Materialização cp_event_log_semantic"
uv run python -m python.local_lab.materialize_cp_event_log_semantic

echo ""
echo "=== Concluído. DuckDB: local/process_intelligence.duckdb | Parquets: data/marts/ ==="
