"""
Alinhamento de candidatos SX3 com regras documentadas nos modelos dbt (CP).

Fonte de verdade inicial: refs em `dbt/models/financeiro/contas_pagar/` e staging `stg_*`.
Permite override via `config/domains.yaml` (chave `mart_override` por domínio).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from app.paths import repo_root

REPO_ROOT = repo_root()

DbtClassification = Literal[
    "ALINHADO_MART",
    "EXISTE_NA_FONTE_NAO_USADO",
    "CANDIDATO_ALTERNATIVO",
    "SEM_COLUNA_NA_FONTE",
    "CONFLITA_COM_REGRA_ATUAL",
    "REQUER_VALIDACAO_NEGOCIO",
]

ConfidenceLevel = Literal["ALTA", "MEDIA", "BAIXA"]


@dataclass(frozen=True)
class MartTriple:
    """Uma coluna (tabela Protheus + campo) associada a uma atividade no mart."""

    activity: str
    table: str
    column: str


# Conjunto primário: colunas efetivamente usadas nos intermediários / conceito mart CP.
# Nomes em MAIÚSCULAS como no SX3 e após UPPER no DuckDB (stg_*).
_DEFAULT_CP_PRIMARY: list[MartTriple] = [
    # int_cp_se2_eventos
    MartTriple("TITULO_CRIADO", "SE2", "E2_EMISSAO"),
    MartTriple("TITULO_CRIADO", "SE2", "E2_DBALTERACAO"),
    MartTriple("TITULO_CANCELADO", "SE2", "E2_STATUS"),
    MartTriple("TITULO_CANCELADO", "SE2", "E2_DBALTERACAO"),
    # int_cp_fk7_eventos
    MartTriple("TITULO_LIBERADO", "FK7", "F7_COD_EVENTO"),
    MartTriple("TITULO_LIBERADO", "FK7", "F7_DATA_EVENTO"),
    MartTriple("TITULO_LIBERADO", "FK7", "F7_HORA_EVENTO"),
    MartTriple("TITULO_LIBERADO", "FK7", "F7_USUARIO"),
    MartTriple("TITULO_LIBERADO", "FK7", "F7_DBALTERACAO"),
    MartTriple("EVENTO_FINANCEIRO_GERADO", "FK7", "F7_COD_EVENTO"),
    MartTriple("EVENTO_FINANCEIRO_GERADO", "FK7", "F7_DATA_EVENTO"),
    MartTriple("EVENTO_FINANCEIRO_GERADO", "FK7", "F7_HORA_EVENTO"),
    MartTriple("EVENTO_FINANCEIRO_GERADO", "FK7", "F7_USUARIO"),
    MartTriple("EVENTO_FINANCEIRO_GERADO", "FK7", "F7_DBALTERACAO"),
    MartTriple("BAIXA_SEM_SE5", "FK7", "F7_COD_EVENTO"),
    MartTriple("BAIXA_SEM_SE5", "FK7", "F7_DATA_EVENTO"),
    MartTriple("BAIXA_SEM_SE5", "FK7", "F7_HORA_EVENTO"),
    MartTriple("BAIXA_SEM_SE5", "FK7", "F7_USUARIO"),
    MartTriple("BAIXA_SEM_SE5", "FK7", "F7_DBALTERACAO"),
    # int_cp_fk2_lancamentos — agregado por caso; timestamps de negócio / fallback técnico
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_DATA_LANCAMENTO"),
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_HORA_LANCAMENTO"),
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_DBALTERACAO"),
    # int_cp_se5_pagamentos
    MartTriple("PAGAMENTO_REALIZADO", "SE5", "E5_DATA_PAGAMENTO"),
    MartTriple("PAGAMENTO_REALIZADO", "SE5", "E5_HORA_PAGAMENTO"),
    MartTriple("PAGAMENTO_REALIZADO", "SE5", "E5_VALOR_PAGO"),
]

# Colunas que existem no staging mas não são eixo de tempo/evento no mart atual para a atividade.
_DEFAULT_CP_ALTERNATIVES: list[MartTriple] = [
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_TIPO_LANCAMENTO"),
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_USUARIO"),
    MartTriple("PAGAMENTO_REALIZADO", "SE5", "E5_USUARIO"),
]

# Casos em que o dicionário sugere um “data field” típico diferente do adotado no mart (V1).
_DEFAULT_CP_CONFLICTS: list[MartTriple] = [
    # Ex.: SX3 pode destacar FK2_DIACTB; mart V1 usa F2_DATA_LANCAMENTO agregado.
    MartTriple("LANCAMENTO_CONTABIL", "FK2", "F2_DIACTB"),
]


@dataclass
class MartRegistry:
    """Registro de colunas mart por atividade, com alternativas e conflitos."""

    primary: set[tuple[str, str, str]] = field(default_factory=set)
    alternatives: set[tuple[str, str, str]] = field(default_factory=set)
    conflicts: set[tuple[str, str, str]] = field(default_factory=set)
    # Todas as colunas que aparecem em qualquer primary (para “usado no mart em algum lugar”).
    all_mart_columns_by_table: dict[str, set[str]] = field(default_factory=dict)

    def _add_triples(self, triples: list[MartTriple], dest: set[tuple[str, str, str]]) -> None:
        for t in triples:
            dest.add((t.activity.upper(), t.table.upper(), t.column.upper()))

    def build_column_index(self) -> None:
        self.all_mart_columns_by_table = {}
        for act, tbl, col in self.primary:
            self.all_mart_columns_by_table.setdefault(tbl, set()).add(col)


def _parse_override_triples(
    block: dict[str, Any],
    kind: str,
) -> list[MartTriple]:
    out: list[MartTriple] = []
    for activity, payload in block.items():
        if not isinstance(payload, dict):
            continue
        rows = payload.get(kind) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            tbl = str(row.get("table", "")).strip().upper()
            col = str(row.get("column", "")).strip().upper()
            if tbl and col:
                out.append(MartTriple(str(activity).upper(), tbl, col))
    return out


def load_mart_registry(
    *,
    domain: str | None = None,
    domains_yaml_path: Path | None = None,
    extra_mart_yaml: Path | None = None,
) -> MartRegistry:
    """
    Carrega MartRegistry para o domínio CP (default) com merges opcionais.

    - domains.yaml: `cp.mart_override` com chaves `primary`, `alternatives`, `conflicts`.
    - extra_mart_yaml: arquivo opcional com o mesmo formato de `mart_override`.
    """
    reg = MartRegistry()
    reg._add_triples(_DEFAULT_CP_PRIMARY, reg.primary)
    reg._add_triples(_DEFAULT_CP_ALTERNATIVES, reg.alternatives)
    reg._add_triples(_DEFAULT_CP_CONFLICTS, reg.conflicts)

    path = domains_yaml_path or (REPO_ROOT / "config" / "domains.yaml")
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        dom = (domain or "cp").lower()
        if dom in data and isinstance(data[dom], dict):
            ov = data[dom].get("mart_override")
            if isinstance(ov, dict):
                for kind, target in (
                    ("primary", reg.primary),
                    ("alternatives", reg.alternatives),
                    ("conflicts", reg.conflicts),
                ):
                    reg._add_triples(_parse_override_triples(ov, kind), target)

    if extra_mart_yaml and extra_mart_yaml.exists():
        with extra_mart_yaml.open(encoding="utf-8") as f:
            ov = yaml.safe_load(f) or {}
        if isinstance(ov, dict):
            for kind, target in (
                ("primary", reg.primary),
                ("alternatives", reg.alternatives),
                ("conflicts", reg.conflicts),
            ):
                reg._add_triples(_parse_override_triples(ov, kind), target)

    reg.build_column_index()
    return reg


def classify_event_candidate(
    *,
    activity: str,
    source_table: str,
    source_column: str,
    duckdb_columns_by_table: dict[str, set[str]],
    mart: MartRegistry,
) -> tuple[DbtClassification, str, ConfidenceLevel]:
    """
    Classifica um candidato (tabela.coluna + atividade inferida).

    Retorna (classificação, justificativa curta, nível de confiança na classificação).
    """
    act = activity.upper()
    tbl = source_table.upper()
    col = source_column.upper()

    cols = duckdb_columns_by_table.get(tbl, set())
    if col not in cols:
        return (
            "SEM_COLUNA_NA_FONTE",
            f"Coluna {tbl}.{col} não encontrada no DuckDB (staging stg_{tbl.lower()}).",
            "BAIXA",
        )

    key = (act, tbl, col)
    if key in mart.primary:
        return (
            "ALINHADO_MART",
            "Coluna listada no mapeamento mart CP (int_cp_*/mart_cp_event_log) para esta atividade.",
            "ALTA",
        )

    if key in mart.conflicts:
        return (
            "CONFLITA_COM_REGRA_ATUAL",
            "Campo frequentemente citado no SX3, mas o mart V1 usa outra coluna de data/agregação.",
            "MEDIA",
        )

    if key in mart.alternatives:
        return (
            "CANDIDATO_ALTERNATIVO",
            "Campo existe no staging e é relacionado ao processo, mas não é o timestamp principal no mart.",
            "MEDIA",
        )

    # Coluna usada no mart para outra atividade (mesma tabela): ambiguidade de negócio.
    activities_for_col: list[str] = []
    for a, t, c in mart.primary:
        if t == tbl and c == col:
            activities_for_col.append(a)
    if activities_for_col and act not in activities_for_col:
        return (
            "REQUER_VALIDACAO_NEGOCIO",
            f"Coluna participa do mart em atividades {sorted(set(activities_for_col))}; "
            f"validar se '{act}' aplica-se no seu catálogo de eventos.",
            "MEDIA",
        )

    # Existe na fonte, não está no conjunto primary desta atividade.
    used_in_mart_elsewhere = col in mart.all_mart_columns_by_table.get(tbl, set())
    if used_in_mart_elsewhere:
        return (
            "EXISTE_NA_FONTE_NAO_USADO",
            "Coluna presente no staging e em outras regras mart, mas não vinculada a esta atividade.",
            "BAIXA",
        )

    return (
        "EXISTE_NA_FONTE_NAO_USADO",
        "Coluna existe no staging; não mapeada no mart CP atual para esta atividade.",
        "BAIXA",
    )


def dbt_models_root_hint() -> Path:
    """Caminho documental para modelos dbt CP (leitura humana / futuro parse)."""
    return REPO_ROOT / "dbt" / "models" / "financeiro" / "contas_pagar"
