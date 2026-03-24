# Arquitetura do repositório (visão pública)

Este ficheiro resume o que o código **efetivamente** implementa. Detalhes em [README.md](README.md), [docs/inventory-src-app.md](docs/inventory-src-app.md) e [docs/adrs/ADR-011-core-architecture-src-app.md](docs/adrs/ADR-011-core-architecture-src-app.md).

## Núcleo único (Python)

| O quê | Onde |
|-------|------|
| Pacote aplicacional | **`src/app/`** (import `app.*`) |
| Empacotamento | **`pyproject.toml`** → `tool.setuptools.packages.find`: `where = ["src"]`, `include = ["app*"]` |
| Pasta `python/` na raiz | **Não existe** — não é o centro do projeto |

## Camadas principais (`app`)

| Camada | Pacote | Função |
|--------|--------|--------|
| Discovery | `app.discovery` | SX3, candidatos, relacionamentos |
| Model | `app.model` | Event log candidato, colunas, agregação |
| Process | `app.process` | Fluxo de processo, ordenação, Mermaid |
| Validation | `app.validation` | Alinhamento dbt, sequências |
| Presentation | `app.presentation` | Exportação de diagramas |
| Pipeline | `app.pipeline` | Orquestração CLI |

Suporte: `app.lab`, `app.core`, `app.connectors`, `app.mining`, `app.simulation`, `app.ai`, `app.config`, `app.utils`.

## Scripts

`scripts/` contém **entrypoints** (bootstrap opcional + chamada a `app.*`). A lógica pesada está em `src/app/`.

## Testes e ferramentas

- **pytest**: `pythonpath = ["src"]` em `pyproject.toml`
- **ruff / coverage**: `src` e `src/app`

## Comandos após instalação editável

```bash
pip install -e .
sian-pipeline
sian-infer-relationships --help
sian-build-flow --help
```

Equivalente sem instalar o pacote: `PYTHONPATH=src python scripts/run_pipeline.py`.
