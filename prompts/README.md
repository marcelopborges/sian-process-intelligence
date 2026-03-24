# Prompts reutilizáveis

Prompts em Markdown para uso com LLMs no contexto do projeto Process Intelligence. Regra geral: **dados e métricas vêm do pipeline; a IA interpreta e comunica** (ADR-006).

| Arquivo | Uso |
|---------|-----|
| [prompt_process_analyst.md](prompt_process_analyst.md) | Agente/analista que responde perguntas com base em resultados de mining. |
| [prompt_sql_copilot.md](prompt_sql_copilot.md) | Auxílio em SQL/dbt para modelos e queries. |
| [prompt_event_mapping.md](prompt_event_mapping.md) | Mapeamento código de evento (ex.: FK7) → nome de atividade. |
| [prompt_bottleneck_analysis.md](prompt_bottleneck_analysis.md) | Interpretação de resultados de análise de gargalos. |
| [prompt_executive_summary.md](prompt_executive_summary.md) | Sumário executivo a partir de métricas e resultados. |

Cada arquivo contém sugestão de system prompt e template de user prompt. Ajustar conforme modelo e ferramenta (Cursor, API própria, etc.).
