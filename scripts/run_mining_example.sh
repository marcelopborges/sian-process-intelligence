#!/usr/bin/env bash
# Exemplo de script para rodar mining (quando implementado).
# Uso: ./scripts/run_mining_example.sh
# Requer: .env configurado, dbt já ter gerado mart_cp_event_log.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Opcional: carregar .env
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# TODO: chamar Python para ler event log e rodar discovery/variants/bottlenecks
# python -m app.mining.discovery ...
echo "Mining pipeline a implementar. Veja src/app/mining/ e docs/roadmap.md."
