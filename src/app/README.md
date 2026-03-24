# Pacote `app` — núcleo oficial

Código Python do **sian-process-intelligence** vive **apenas** aqui (`src/app/`). Não há pacote paralelo `python/` na raiz do repositório.

## Layout

```
app/
  discovery/      # SX3, heurísticas, inferência de eventos e relacionamentos (relationship_runner)
  model/          # Event log candidato, classificação, agregação, LLM opcional
  process/        # Fluxo (build_flow, ordering, flow_from_event_log)
  validation/     # dbt_alignment, validate_*
  presentation/   # Mermaid, export_diagram
  pipeline/       # runner CLI (pipeline semântico)
  config/         # domain_config, settings
  lab/            # laboratório DuckDB / Parquet
  core/           # schemas
  connectors/     # leitura de event log
  mining/         # PM4Py (pós–mart)
  simulation/     # SimPy
  ai/             # LLM sobre resultados
  utils/
  paths.py
```

## Imports

```python
from app.discovery.sx3_loader import load_sx3_csv
from app.pipeline.runner import run_pipeline
```

Instalação: na raiz do repo, `pip install -e .` (ver `pyproject.toml`).
