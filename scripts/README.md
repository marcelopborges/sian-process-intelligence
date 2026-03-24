# Scripts operacionais

Executar a partir da **raiz do repositório** (`python scripts/...`). O código-fonte principal está em **`src/app/`** (importável como `app.*` após `pip install -e .` ou com `PYTHONPATH=src`).

### Comandos de consola (após `pip install -e .`)

Definidos em `pyproject.toml` → `[project.scripts]`; implementação só em `src/app/`.

| Comando | Módulo |
|---------|--------|
| `sian-pipeline` | `app.pipeline.runner` |
| `sian-infer-relationships` | `app.discovery.relationship_runner` |
| `sian-build-flow` | `app.process.flow_from_event_log` |

## Pipeline único

| Script | Descrição |
|--------|-----------|
| `run_pipeline.py` | Pipeline completo (padrão: `--build-event-log --build-process-flow --validate`). |
| `run_discovery.py` | Apenas candidatos SX3 + DuckDB (sem event log / fluxo). |
| `run_model.py` | Inclui `--build-event-log`. |
| `run_process.py` | Event log + fluxo (Mermaid). |
| `run_validation.py` | Validação offline a partir de JSONs em `--output`. |

```bash
python scripts/run_pipeline.py
```

Saída padrão: `data/outputs/sx3_semantic/` (use `-o` / `--output` para alterar).

## Inferência a partir do SX3 (Protheus)

### `infer_relationships_from_sx3.py`

- **Entrada**: CSV SX3 (`--sx3` ou `--sx3-csv`), DuckDB com `stg_*`.
- **Saída**: `data/outputs/sx3_semantic/sx3_relationship_suggestions.{json,md}`; tabela `sx3_relationship_suggestions`.
- **Parâmetros úteis**: `--min-confidence` (default 0.6), `--duckdb-path`, `-o`.

```bash
python scripts/infer_relationships_from_sx3.py --sx3 data/others/SX3010_202603231122.csv
```

### `infer_events_from_sx3.py`

Wrapper fino para o mesmo CLI que `app.pipeline.runner` (compatibilidade com chamadas antigas). Preferência: `python scripts/run_pipeline.py`.

- **Pipeline**: heurística → filtro de tabelas (`--domain` / `--include-tables`) → `--min-score` → `--top-n-per-table` → `dbt_alignment` → `column_role` → opcional `--build-event-log` → opcional `--use-llm` (desligado com `--build-event-log`).
- **Saída**: `sx3_event_candidates.json` + tabela `sx3_event_candidates`; com `--build-event-log`: `event_log_candidates.json` + tabela `event_log_candidates`.

**Módulos (`app.*`):**

| Caminho | Função |
|---------|--------|
| `app.discovery.sx3_loader` | Leitura e índice SX3. |
| `app.discovery.relationship_inferer` | Heurística de relacionamentos. |
| `app.validation.dbt_alignment` | Classificação vs mart CP (`mart_override` em `config/domains.yaml`). |
| `app.model.classify_columns` | Papel da coluna: EVENT_TIME, ATTRIBUTE, … |
| `app.model.build_event_log` / `event_aggregation` | Agregação por activity → event log candidato. |
| `app.config.domain_config` | Resolução de `--domain` / listas de tabelas. |
| `app.model.llm_enrichment` | Opcional: texto semântico via OpenAI (`OPENAI_API_KEY`). |

**Variáveis de ambiente (LLM opcional):**

- `OPENAI_API_KEY`: obrigatória para chamada real à API.
- `OPENAI_MODEL`: default `gpt-4o-mini`.

### `build_process_flow.py` (só fluxo / Mermaid)

Regenera `process_flow.json` e `process_flow.md` a partir de `event_log_candidates.json` (sem reprocessar SX3):

```bash
python scripts/build_process_flow.py \
  --input data/outputs/sx3_semantic/event_log_candidates.json \
  --duckdb-path local/process_intelligence.duckdb \
  -o data/outputs/sx3_semantic
```

Ou use `run_pipeline.py` / `infer_events_from_sx3.py` com `--build-event-log --build-process-flow`.

## Segurança

Não commitar credenciais; usar `.env` e variáveis de ambiente.
