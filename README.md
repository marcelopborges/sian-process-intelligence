# sian-process-intelligence

Plataforma de **Process Intelligence** voltada a processos organizacionais, iniciando por **Contas a Pagar** no ecossistema TOTVS Protheus. Repositório estruturado como laboratório técnico com visão de produto reutilizável.

---

## Visão do projeto

Oferecer uma base analítica e de mineração de processos que permita:

- Construir tabelas analíticas de processo a partir de dados do Protheus no BigQuery
- Gerar event logs padronizados para Process Mining
- Executar mineração de processos (descoberta, variantes, gargalos) com Python/PM4Py
- Simular cenários de processo com SimPy
- Integrar IA para documentação assistida, interpretação de variantes/gargalos, recomendações e futura atuação como agente analista

O projeto **não** está acoplado ao Cortex nem ao Argos neste momento; a arquitetura é preparada para futura integração com ambos.

---

## Problema que resolve

- **Dados de processo fragmentados**: informações de contas a pagar (e futuramente outros processos) espalhadas em tabelas Protheus (SE2, FK7, FK2, SE5) sem um modelo analítico unificado.
- **Falta de visibilidade de fluxo**: dificuldade para entender variantes de processo, tempos e gargalos de forma sistemática.
- **Decisões sem base quantitativa**: pouca capacidade de simular cenários e priorizar melhorias com dados.
- **Documentação e interpretação manuais**: custo alto para manter documentação e análises atualizadas; oportunidade de amplificar com IA.

---

## Escopo inicial

- **Processo**: Contas a Pagar no Protheus (cadeia SE2 → FK7 → FK2 → SE5).
- **Stack**: BigQuery (dados), dbt (transformação), Python (mining, simulação, IA).
- **Entregas**:
  - Modelos dbt para case base e event log de contas a pagar
  - Pipelines Python para discovery, variantes, gargalos (PM4Py) e simulação (SimPy)
  - Camada de IA para interpretação e recomendações (fases incrementais)
  - Documentação, ADRs e prompts reutilizáveis

---

## Escopo futuro

- Outros processos: Compras, RH, Controladoria (arquitetura preparada).
- Integração com Cortex (orquestração) e Argos (observabilidade).
- Agente analista de processos com acesso a dados e ferramentas.
- Camada semântica evoluída e métricas de processo padronizadas.

---

## Arquitetura de alto nível

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SIAN Process Intelligence                         │
├─────────────────────────────────────────────────────────────────────────┤
│  BigQuery (dados Protheus)                                               │
│       │                                                                  │
│       ▼                                                                  │
│  dbt (transformação)  →  case_base + event_log (modelo universal)        │
│       │                                                                  │
│       ▼                                                                  │
│  Python: mining (PM4Py) │ simulation (SimPy) │ connectors │ core         │
│       │                                                                  │
│       ▼                                                                  │
│  Camada IA: interpretação, recomendações, documentação assistida        │
│       │                                                                  │
│       ▼                                                                  │
│  (futuro) Cortex / Argos                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Fonte**: BigQuery com dados já carregados do Protheus.
- **Transformação**: dbt produz três saídas distintas — **mart_cp_case_base** (TABLE, estático), **mart_cp_event_log** (TABLE, Process Mining, com event_timestamp_adjusted e timestamp_confiabilidade), **mart_cp_ap_operacional** (VIEW, dinâmica para aging/SLA). 1 caso = 1 título SE2; case_id = chave de 7 campos (E2_FILIAL, E2_PREFIXO, E2_NUM, E2_PARCELA, E2_TIPO, E2_FORNECE, E2_LOJA) com TRIM.
- **Análise**: Python lê event logs (coluna efetiva para mining: event_timestamp_adjusted), aplica PM4Py e SimPy.
- **IA**: camada de interpretação e recomendação sobre resultados da mineração; não substitui a modelagem.

---

## Stack

| Camada        | Tecnologia |
|---------------|------------|
| Dados         | BigQuery   |
| Transformação | dbt        |
| Process Mining| PM4Py      |
| Simulação     | SimPy      |
| Linguagem     | Python 3.11+ |
| IA            | LLMs (integração futura; abstração em `src/app/ai/`) |

---

## Roadmap inicial

1. **Fase 0 (bootstrap)**: Estrutura do repositório, ADRs, documentação, esqueletos dbt e Python.
2. **Fase 1**: Modelos dbt de contas a pagar validados (int + mart case_base + event_log).
3. **Fase 2**: Pipelines Python de discovery, variantes e gargalos com PM4Py.
4. **Fase 3**: Simulação de cenários com SimPy e primeiros prompts de IA (interpretação/sumarização).
5. **Fase 4**: Recomendações assistidas por IA e preparação para integração Cortex/Argos.

Detalhes em [docs/roadmap.md](docs/roadmap.md).

---

## Integração de IA

A IA atua como **amplificador** da análise, não como fonte primária de verdade:

- **Onde ajuda**: documentação, interpretação de variantes/gargalos, sumarização executiva, recomendações sugeridas, copiloto de SQL.
- **Onde não substitui**: modelagem de dados, definição de regras de negócio, validação de métricas.

Estratégia em fases em [docs/ai-integration.md](docs/ai-integration.md) e [docs/ai-strategy.md](docs/ai-strategy.md). Prompts reutilizáveis em [prompts/](prompts/).

---

## Relação futura com Cortex e Argos

- **Cortex**: orquestração de pipelines, agendamento, possível exposição de capabilities de Process Intelligence como serviços.
- **Argos**: observabilidade, métricas e alertas sobre pipelines e qualidade de dados.
- Este repositório permanece **desacoplado**; a integração será feita por contratos bem definidos (APIs, eventos ou artefatos compartilhados).

---

## Princípios de design

- **Desacoplamento**: capacidade reutilizável; sem dependência direta de Cortex/Argos no início.
- **Event log universal**: case_id, activity, event_timestamp_adjusted, timestamp_confiabilidade (NEGOCIO/TECNICO); valor observado vs inferido no case base (vl_pago_e_inferido).
- **IA como camada**: interpretação e recomendação sobre dados e métricas já validados.
- **Iteração**: camada semântica mínima no início, evolução conforme necessidade.
- **Rastreabilidade**: ADRs para decisões arquiteturais; documentação e glossário em `docs/`.

---

## Estrutura do repositório

```
├── README.md
├── docs/                 # Documentação (vision, architecture, domain, glossary, roadmap)
├── adrs/                 # Architecture Decision Records
├── dbt/                  # Projeto dbt (models/financeiro/contas_pagar)
├── src/app/              # Pacote Python único (pipeline por camadas; ver secção abaixo)
├── data/
│   ├── raw/              # Entradas brutas (convênio de pastas)
│   ├── staging/          # Dados intermediários locais
│   └── outputs/          # Artefatos gerados (event_log, process_flow, validation, sx3_semantic)
├── notebooks/            # Jupyter notebooks exploratórios
├── config/               # Configurações (domains.yaml, dbt, env)
├── tests/                # Testes unitários e de integração
├── prompts/              # Prompts reutilizáveis para LLMs
├── scripts/              # CLIs finas (run_pipeline, infer_*, laboratório DuckDB)
├── pyproject.toml
├── requirements.txt
└── Makefile
```

### Arquitetura Python (pipeline)

O código vive em **`src/app/`** e segue o fluxo:

**DISCOVERY → MODEL → PROCESS → VALIDATION → PRESENTATION**

| Camada | Pacote | Papel |
|--------|--------|--------|
| Discovery | `app.discovery` | SX3, heurísticas, inferência de eventos e relacionamentos |
| Model | `app.model` | Event log candidato, classificação de colunas, agregação |
| Process | `app.process` | Ordenação, construção do fluxo (arestas, recuperação de eventos) |
| Validation | `app.validation` | Alinhamento dbt/staging, validação de sequências |
| Presentation | `app.presentation` | Mermaid, exportação de diagramas |
| Orquestração | `app.pipeline` | CLI única (`run_pipeline`) com `--input` / `--output` |

Laboratório local (BigQuery → Parquet → DuckDB): `app.lab`. Utilidades: `app.paths`, `app.config`.

**Comando principal (pipeline completo — event log + fluxo + relatório de validação):**

```bash
python scripts/run_pipeline.py
```

Equivale a passar `--build-event-log --build-process-flow --validate`. Sem argumentos extra, os artefatos vão para `data/outputs/sx3_semantic/` (ajuste com `-o` / `--output`).

**Alternativa (pacote instalável):** `pip install -e .` e então `python -m app.pipeline` (mesmos argumentos do runner).

Scripts por etapa: `scripts/run_discovery.py`, `run_model.py`, `run_process.py`, `run_validation.py` (validação offline a partir de JSONs já gerados).

---

## Como começar

1. Clone o repositório e crie um ambiente virtual (Python 3.11+).
2. Instale dependências: `pip install -r requirements.txt` ou `uv sync`.
3. Configure variáveis de ambiente: copie `.env.example` para `.env` e preencha (BigQuery, etc.).
4. Execute o dbt (quando os modelos estiverem implementados): `make dbt-run`.
5. Consulte [docs/roadmap.md](docs/roadmap.md) e os TODOs nos arquivos para próximos passos.

---

## Governança semântica: SX3 → candidatos de evento e relacionamentos

Scripts Python leem o **dicionário SX3** (export CSV do Protheus), aplicam heurísticas e **cruzam com o que existe no DuckDB** (tabelas `stg_*` do laboratório local) e com **regras documentadas dos modelos dbt** de Contas a Pagar (`dbt/models/financeiro/contas_pagar/`). Servem como **checklist de governança** — não substituem o `mart_cp_event_log`.

### Pré-requisitos

- Python **3.11+**, ambiente virtual recomendado.
- Dependências: `pip install -r requirements.txt` (inclui `duckdb`, `pandas`, `pyyaml`).
- **Arquivo SX3 (CSV)** com colunas mínimas `X3_ARQUIVO`, `X3_CAMPO` (e metadados usuais). Local padrão no repositório: `data/others/SX3010_202603231122.csv` (ajuste ao seu export).
- **DuckDB local** com tabelas `stg_se2`, `stg_fk7`, `stg_fk2`, `stg_se5` (nomes em schema `main`). Caminho padrão: `local/process_intelligence.duckdb` (definido em `src/app/lab/config.py`). Sem esse banco, o script **não roda** — é necessário carregar o staging no laboratório antes.

### Comandos (a partir da raiz do repositório)

**Relacionamentos (SX3 + heurística de colunas iguais / F3):**

```bash
python scripts/infer_relationships_from_sx3.py \
  --sx3 data/others/SX3010_202603231122.csv \
  --duckdb-path local/process_intelligence.duckdb \
  -o data/outputs/sx3_semantic
```

**Candidatos de evento (recomendado para CP — menos ruído):**

```bash
python scripts/infer_events_from_sx3.py \
  --sx3 data/others/SX3010_202603231122.csv \
  --duckdb-path local/process_intelligence.duckdb \
  --domain cp \
  --min-score 0.6 \
  --top-n-per-table 10 \
  -o data/outputs/sx3_semantic
```

Filtro explícito de tabelas (sobrescreve `--domain`):

```bash
python scripts/infer_events_from_sx3.py \
  --sx3 ./data/others/SX3010_202603231122.csv \
  --include-tables SE2,FK7,FK2,SE5 \
  --min-score 0.6 \
  --top-n-per-table 10
```

Opcional — enriquecimento com LLM (apenas texto / confiança; **não** infere joins). Requer `OPENAI_API_KEY`; sem chave, gera descrição por regras e registra em auditoria:

```bash
export OPENAI_API_KEY=sk-...
python scripts/infer_events_from_sx3.py --domain cp --use-llm
```

**Event log candidato (1 linha por activity, timestamp + atributos)** — sem LLM; ignora `--top-n-per-table` para não perder colunas `EVENT_TIME`:

```bash
python scripts/infer_events_from_sx3.py \
  --sx3 data/others/SX3010_202603231122.csv \
  --duckdb-path local/process_intelligence.duckdb \
  --domain cp \
  --min-score 0.5 \
  --build-event-log \
  --top-attributes-per-event 8 \
  -o data/outputs/sx3_semantic
```

Gera `data/outputs/sx3_semantic/event_log_candidates.json` e a tabela DuckDB `event_log_candidates`.

**Fluxo visual (Mermaid) a partir do event log candidato:**

```bash
python scripts/infer_events_from_sx3.py \
  --sx3 data/others/SX3010_202603231122.csv \
  --duckdb-path local/process_intelligence.duckdb \
  --domain cp \
  --build-event-log \
  --build-process-flow \
  -o data/outputs/sx3_semantic
```

Saídas: `process_flow.json` (nós, arestas, `unreliable_events`, diagrama), `process_flow.md` (bloco Mermaid), tabela DuckDB `process_flow_snapshot`. Ordenação alinhada à macro dbt `cp_event_order`.

### Onde ficam os outputs

| Artefato | Descrição |
|----------|-----------|
| `data/outputs/sx3_semantic/sx3_event_candidates.json` | Candidatos por coluna (inclui `column_role`: EVENT_TIME, ATTRIBUTE, …). |
| `data/outputs/sx3_semantic/event_log_candidates.json` | **Com `--build-event-log`:** 1 registro por `activity` com `event_time` + `attributes`. |
| `data/outputs/sx3_semantic/sx3_event_candidates.md` | Visão tabular (top N). |
| `data/outputs/sx3_semantic/sx3_relationship_suggestions.json` / `.md` | Sugestões de relacionamento. |
| DuckDB: `sx3_event_candidates` | Candidatos por coluna (`column_role`, alinhamento dbt, LLM opcional). |
| DuckDB: `event_log_candidates` | **Com `--build-event-log`:** evento agregado por activity. |
| DuckDB: tabela `sx3_relationship_suggestions` | Relacionamentos inferidos. |

### Domínio CP (`config/domains.yaml`)

O arquivo `config/domains.yaml` declara o domínio `cp` (tabelas SE2, FK7, FK2, SE5). A CLI `--domain cp` restringe a inferência a essas tabelas. É possível estender com `mart_override` (ver comentários no YAML) para futuras colunas mart.

### Como interpretar os resultados

- **`heuristic_score`**: confiança da heurística por palavras-chave no SX3 (0–1); não é verdade de negócio.
- **`dbt_classification`**: cruzamento com regras dos intermediários/mart CP, por exemplo:
  - **ALINHADO_MART**: coluna alinhada ao uso em `int_cp_*` / conceito do `mart_cp_event_log`.
  - **SEM_COLUNA_NA_FONTE**: campo não aparece no `stg_*` carregado no DuckDB.
  - **CANDIDATO_ALTERNATIVO** / **CONFLITA_COM_REGRA_ATUAL** / **REQUER_VALIDACAO_NEGOCIO** / **EXISTE_NA_FONTE_NAO_USADO**: ver justificativa curta no JSON.
- **`confidence_level`** (ALTA/MEDIA/BAIXA): confiança na **classificação de alinhamento**, não no processo real.
- **`semantic_description`**: texto explicativo (regras ou LLM se `--use-llm`).

### Limitações atuais

- Heurística por keywords: pode perder eventos ou gerar falsos positivos se o texto SX3 for ambíguo.
- Alinhamento dbt usa **registro fixo** em `src/app/validation/dbt_alignment.py` + opcional `mart_override` no YAML — não executa `dbt parse` automaticamente (evolução futura).
- LLM opcional depende de rede e `OPENAI_API_KEY`; não cria regras de processo nem joins.

### Exemplo de registro no JSON (candidato enriquecido)

```json
{
  "candidate_id": "TITULO_CRIADO:SE2.E2_EMISSAO:0",
  "activity": "TITULO_CRIADO",
  "event_type_suggested": "TITULO_CRIADO",
  "source_table": "SE2",
  "source_column": "E2_EMISSAO",
  "column_role": "EVENT_TIME",
  "heuristic_score": 0.85,
  "reason": "keyword_match:EMISSAO;expected_table_boost:0.20",
  "dbt_classification": "ALINHADO_MART",
  "justification": "Coluna listada no mapeamento mart CP (int_cp_*/mart_cp_event_log) para esta atividade.",
  "confidence_level": "ALTA",
  "semantic_description": "Atividade sugerida: TITULO_CRIADO (tabela SE2, campo E2_EMISSAO). Classificação dbt: ALINHADO_MART. …",
  "llm_revised_confidence": null,
  "llm_audit": null,
  "created_at_utc": "2026-03-16T12:00:00+00:00"
}
```

### Exemplo de registro no JSON (`event_log_candidates.json`, `--build-event-log`)

```json
{
  "activity": "PAGAMENTO_REALIZADO",
  "event_status": "OK",
  "event_time": { "table": "SE5", "column": "E5_DATA_PAGAMENTO" },
  "attributes": [
    { "table": "SE5", "column": "E5_VALOR_PAGO" },
    { "table": "SE5", "column": "E5_BANCO" }
  ],
  "source_tables": ["SE5"],
  "confidence": "ALTA",
  "dbt_alignment": "ALINHADO"
}
```

Detalhes técnicos adicionais: [scripts/README.md](scripts/README.md).

---

## Próximos passos

Após o bootstrap, priorize:

1. **Dados**: Configurar `.env`, apontar stg_* para tabelas reais no BigQuery e rodar `dbt run` / `dbt test`.
2. **Mining**: Implementar leitura do event log e funções em `src/app/mining/` (PM4Py).
3. **Validação**: Validar case base e event log com área de negócio; documentar mapeamento de atividades em `docs/glossary.md`.

Detalhes em [docs/next-steps.md](docs/next-steps.md) e [docs/roadmap.md](docs/roadmap.md).

## Licença e responsabilidade

Projeto interno. Dados e regras de negócio devem ser validados com as áreas responsáveis antes de uso em produção.
