# ADR-011: Núcleo oficial do código em `src/app` (pacote `app`)

**Status**: Aceito (repositório)  
**Data**: 2026-03  
**Substitui / complementa**: ADR-001 (repositório dedicado), documentação de pipeline em README.

## Problema

O repositório chegou a apresentar **dois centros de código Python**:

- uma árvore `python/` na raiz (pacote plano por domínio técnico: `sx3`, `validation`, `local_lab`, …);
- uma árvore `src/app/` orientada a **camadas de pipeline** (discovery, model, process, …).

Isso gerava ambiguidade: imports (`python.*` vs `app.*`), duplicação de lógica, `pyproject.toml` incerto sobre o que empacotar, e risco de notebooks e scripts reforçarem caminhos inconsistentes.

## Decisão

1. **`src/app/` é o único núcleo oficial** do código Python do projeto. O pacote instalável é **`app`** (namespace `app.*`).

2. A pasta **`python/` foi descontinuada e removida** do repositório após migração do conteúdo para `src/app/`. Não há segunda cópia “viva” da mesma lógica em paralelo.

3. A organização segue **camadas de responsabilidade** (ver README, secção Arquitetura), com pacotes de suporte claramente nomeados (`lab`, `core`, `connectors`, `mining`, `simulation`, `ai`, `pipeline`).

## Mapeamento conceitual (legado `python/` → `src/app/`)

Classificação usada na migração (por responsabilidade, não só por nome de pasta antiga):

| Antigo (`python/`) | Camada / papel | Destino atual (`app.*`) |
|--------------------|----------------|-------------------------|
| `sx3/` | Discovery (metadados SX3, relacionamentos) | `app.discovery` |
| `validation/` (dbt, roles, event log builder, LLM enrich) | Model + validation | `app.validation`, `app.model` |
| `local_lab/` | Laboratório local (BQ → Parquet → DuckDB) | `app.lab` |
| `utils/` | Utilitários | `app.utils` |
| `core/` | Contratos / esquemas compartilhados | `app.core` |
| `connectors/` | Leitura de event log / fontes | `app.connectors` |
| `mining/` | PM4Py (pós–event log mart) | `app.mining` (pacote de análise; não confundir com `app.process` de fluxo SX3) |
| `simulation/` | SimPy | `app.simulation` |
| `ai/` | LLM / texto sobre resultados | `app.ai` |

**Nota:** `app.process` no pipeline semântico SX3 significa **construção do fluxo de processo** (ordenação, arestas, Mermaid), não “Process Mining” no sentido PM4Py. Mineração clássica permanece em `app.mining` até eventual consolidação futura.

## Alternativas consideradas

| Alternativa | Por que não foi adotada como estado final |
|-------------|---------------------------------------------|
| Manter `python/` e `src/app/` em paralelo | Duplicidade, dois estilos de import, erro humano garantido. |
| Empacotar só `python/` | `src/` layout é padrão moderno e evita colisão com scripts. |
| Dividir vários pacotes PyPI no mesmo repo | Complexidade desnecessária na fase de estudo; um pacote `app` basta. |

## Consequências

- **Imports únicos**: `from app.discovery...`, `from app.model...`, etc.; testes usam `pythonpath = src` ou `pip install -e .`.
- **`pyproject.toml`**: `packages.find` em `where = ["src"]`, `include = ["app*"]`.
- **Scripts** (`scripts/`): devem permanecer **finos** — bootstrap de `sys.path` ou ambiente virtual, delegação a `app.pipeline` ou módulos específicos.
- **Notebooks**: devem assumir `app` instalado em modo editável ou `PYTHONPATH=src`, alinhado ao núcleo único.
- **Rastreabilidade**: mudanças arquiteturais futuras devem atualizar este ADR ou criar ADR filho.

## Critérios de sucesso

- Nenhum import `python.*` no código versionado.
- Uma única árvore fonte em `src/app/`.
- Documentação (README + este ADR) deixa explícito o núcleo e o pipeline.
