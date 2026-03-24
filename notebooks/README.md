# Notebooks

Jupyter notebooks para análises exploratórias e demonstrações:

- **`00_process_intelligence_walkthrough.ipynb`**: guia didático do pipeline (DISCOVERY → MODEL → PROCESS → VALIDATION → PRESENTATION), usando apenas imports `app.*` e artefatos em `data/outputs/sx3_semantic` (ou `output/sx3_semantic`). Requer `pip install -e .` na raiz do repositório.
- **Contas a pagar**: leitura do event log, discovery, variantes e gargalos (quando os modelos dbt estiverem populados).
- **Simulação**: exemplo de cenário SimPy e comparação com métricas reais.

Recomendação: manter notebooks versionados sem outputs pesados (clear output antes do commit) ou usar scripts em `scripts/` / pacote `app` para pipelines reproduzíveis e rodar notebooks apenas para exploração.
