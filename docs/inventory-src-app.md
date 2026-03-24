# Inventário: núcleo `src/app` (verificação)

## Estado da pasta `python/`

**Não existe** na raiz do repositório. O conteúdo histórico foi migrado para `src/app/`; não há pacote paralelo nem duplicação de módulos.

## Classificação por domínio (implementação atual)

| Domínio | Local em `app` |
|---------|----------------|
| discovery | `app.discovery` (incl. `relationship_runner`, `sx3_loader`, `infer_events`, …) |
| model | `app.model` |
| process | `app.process` (incl. `flow_from_event_log` para CLI de fluxo) |
| validation | `app.validation` |
| presentation | `app.presentation` |
| config | `app.config` |
| utils | `app.utils` |
| core | `app.core` |
| connectors | `app.connectors` |
| lab | `app.lab` |
| mining | `app.mining` |
| simulation | `app.simulation` |
| ai | `app.ai` |
| pipeline | `app.pipeline` |

## Empacotamento

- `pyproject.toml`: `tool.setuptools.packages.find` → `where = ["src"]`, `include = ["app*"]`.
- `[project.scripts]`: ver `pyproject.toml` e `scripts/README.md`.
