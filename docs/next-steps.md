# Próximos passos — Após o bootstrap

Checklist prático para começar a implementação após o bootstrap do repositório.

## 1. Ambiente e credenciais

- [ ] Criar ambiente virtual (Python 3.11+): `python -m venv .venv` e ativar.
- [ ] Instalar dependências: `pip install -r requirements.txt` ou `uv sync`.
- [ ] Copiar `.env.example` para `.env` e preencher `BQ_PROJECT_ID`, `BQ_DATASET_RAW`, `BQ_DATASET_ANALYTICS`.
- [ ] Configurar autenticação BigQuery (OAuth ou service account) para rodar dbt.

## 2. Dados no BigQuery

- [ ] Confirmar que as tabelas SE2, FK7, FK2, SE5 (ou equivalentes) existem no BigQuery e obter dataset/tabela.
- [ ] Atualizar os modelos `dbt/models/staging/stg_*.sql` para fazer `select` da fonte real (ex.: `{{ source('raw_protheus', 'se2') }}`) e mapear colunas reais.
- [ ] Rodar `dbt run` e corrigir erros de coluna/tipo até todos os modelos verdes.
- [ ] Adicionar testes dbt em `dbt/models/.../schema.yml` (unique, not_null, accepted_values para activity).
- [ ] Validar amostra do `mart_cp_event_log` com área de negócio (nomes de atividades, caso de uso).

## 3. Python: connectors e mining

- [ ] Implementar `read_event_log_from_bigquery` em `python/connectors/event_log_reader.py` (usar google-cloud-bigquery e pandas).
- [ ] Implementar `discover_process_model` e helpers em `python/mining/discovery.py` (PM4Py).
- [ ] Implementar `get_variants` e `variant_summary` em `python/mining/variants.py`.
- [ ] Implementar `compute_bottlenecks` e `bottleneck_summary` em `python/mining/bottlenecks.py`.
- [ ] Criar notebook em `notebooks/` que lê o mart, roda mining e exibe variantes/gargalos.

## 4. Simulação e IA

- [ ] Implementar `run_simulation` e `build_scenario_from_event_log` em `python/simulation/scenarios.py` (SimPy).
- [ ] Implementar `complete` em `python/ai/llm_client.py` (leitura de env, chamada à API do provedor).
- [ ] Implementar `interpret_variants` e `interpret_bottlenecks` em `python/ai/analysis.py` usando os prompts em `prompts/`.
- [ ] Implementar `generate_recommendations` em `python/ai/recommendations.py` com guardrails.

## 5. Qualidade e CI

- [ ] Rodar `make lint` e `make format`; corrigir avisos.
- [ ] Rodar `pytest tests/` e garantir que todos passam; adicionar testes para novas funções.
- [ ] (Opcional) Configurar CI (GitHub Actions ou similar) para lint, format e pytest em todo PR.

## 6. Documentação e produto

- [ ] Atualizar `docs/domain-contas-a-pagar.md` com mapeamento real de atividades (FK7 → nomes) após validação.
- [ ] Atualizar `docs/glossary.md` com quaisquer novos termos.
- [ ] Quando houver definição de contrato com Cortex/Argos, documentar em `docs/architecture.md` e criar ADR se necessário.

## Ordem sugerida

1 → 2 (dados e dbt) primeiro; depois 3 (mining); em seguida 4 (simulação e IA) e 5 (qualidade). A fase 6 é contínua.
