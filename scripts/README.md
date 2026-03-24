# Scripts operacionais

Scripts executados a partir da **raiz do repositório** (`python scripts/...`).

## Inferência a partir do SX3 (Protheus)

### `infer_relationships_from_sx3.py`

- **Entrada**: CSV SX3 (`--sx3` ou `--sx3-csv`), DuckDB com `stg_*`.
- **Saída**: `output/sx3_semantic/sx3_relationship_suggestions.{json,md}`; tabela `sx3_relationship_suggestions`.
- **Parâmetros úteis**: `--min-confidence` (default 0.6), `--duckdb-path`, `-o`.

```bash
python scripts/infer_relationships_from_sx3.py --sx3 data/others/SX3010_202603231122.csv
```

### `infer_events_from_sx3.py`

- **Entrada**: CSV SX3, DuckDB com `stg_*`.
- **Pipeline**: heurística → filtro de tabelas (`--domain` / `--include-tables`) → `--min-score` → `--top-n-per-table` → `dbt_alignment` → `column_role` → opcional `--build-event-log` (agregação 1/activity) → opcional `--use-llm` (desligado automaticamente com `--build-event-log`).
- **Saída**: `sx3_event_candidates.{json,md}` + tabela `sx3_event_candidates`; com `--build-event-log`: `event_log_candidates.json` + tabela `event_log_candidates`.

**Módulos Python:**

| Caminho | Função |
|---------|--------|
| `python/sx3/sx3_loader.py` | Leitura e índice SX3. |
| `python/sx3/relationship_inferer.py` | Heurística de relacionamentos. |
| `python/validation/dbt_alignment.py` | Classificação vs mart CP (regras + `mart_override` em `config/domains.yaml`). |
| `python/validation/column_role.py` | Papel da coluna: EVENT_TIME, ATTRIBUTE, IDENTIFIER, STATUS, UNKNOWN. |
| `python/validation/event_log_builder.py` | Agregação por activity → event log candidato. |
| `python/validation/domain_config.py` | Resolução de `--domain` / listas de tabelas. |
| `python/validation/llm_enrichment.py` | Opcional: texto semântico via OpenAI (`OPENAI_API_KEY`). |

**Variáveis de ambiente (LLM opcional):**

- `OPENAI_API_KEY`: obrigatória para chamada real à API.
- `OPENAI_MODEL`: default `gpt-4o-mini`.

### `build_process_flow.py` (só fluxo / Mermaid)

Regenera `process_flow.json` e `process_flow.md` a partir de `event_log_candidates.json` (sem reprocessar SX3):

```bash
python scripts/build_process_flow.py \
  --input output/sx3_semantic/event_log_candidates.json \
  --duckdb-path local/process_intelligence.duckdb \
  -o output/sx3_semantic
```

Ou use `infer_events_from_sx3.py` com `--build-event-log --build-process-flow` no mesmo comando.

## Segurança

Não commitar credenciais; usar `.env` e variáveis de ambiente.
