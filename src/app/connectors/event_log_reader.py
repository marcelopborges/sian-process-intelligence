"""
Leitura de event log a partir de BigQuery ou arquivo (Parquet, CSV, XES).

Responsabilidade: obter um DataFrame no formato do event log de Contas a Pagar:
- case_id, activity, event_timestamp_original, event_order, event_timestamp_adjusted,
  timestamp_confiabilidade (+ resource opcional).
Para Process Mining, usar event_timestamp_adjusted como timestamp efetivo (ordenação estável).
Ver app.core.schemas e mart_cp_event_log.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# TODO: importar pandas e google.cloud.bigquery quando implementar
# import pandas as pd
# from google.cloud import bigquery


def read_event_log_from_bigquery(
    project_id: str,
    dataset: str,
    table: str,
    **kwargs: Any,
) -> Any:
    """
    Carrega event log a partir de uma tabela BigQuery (ex.: mart_cp_event_log).

    Args:
        project_id: Projeto GCP.
        dataset: Dataset (ex.: analytics_process).
        table: Nome da tabela (ex.: mart_cp_event_log).
        **kwargs: Argumentos adicionais para o client BigQuery (ex.: filters).

    Returns:
        DataFrame com colunas: case_id, activity, event_timestamp_original,
        event_order, event_timestamp_adjusted, timestamp_confiabilidade (e opcionais).
        Para mining, ordenar por case_id, event_timestamp_adjusted.

    TODO:
        - Implementar query e conversão para pandas.
        - Garantir timezone e tipos (timestamp como datetime).
    """
    raise NotImplementedError("BigQuery reader a implementar conforme dados reais.")


def read_event_log_from_file(path: Path | str) -> Any:
    """
    Carrega event log a partir de arquivo (Parquet, CSV ou XES).

    Args:
        path: Caminho para o arquivo.

    Returns:
        DataFrame no formato do event log (colunas obrigatórias incluem
        event_timestamp_adjusted e timestamp_confiabilidade quando aplicável).

    TODO:
        - Suportar .parquet, .csv.
        - XES via PM4Py: pm4py.read_xes(str(path)) e mapear para colunas
          event_timestamp_adjusted (ou timestamp), timestamp_confiabilidade.
    """
    raise NotImplementedError("File reader a implementar (Parquet/CSV/XES).")
