"""Carrega config/domains.yaml para filtros por domínio (CP, etc.)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.paths import repo_root

REPO_ROOT = repo_root()
DEFAULT_DOMAINS_PATH = REPO_ROOT / "config" / "domains.yaml"


@dataclass(frozen=True)
class DomainSpec:
    """Definição de um domínio (ex.: contas a pagar)."""

    domain_id: str
    label: str
    tables: tuple[str, ...]
    description: str = ""
    mart_override: dict[str, Any] | None = None


def load_domains_yaml(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_DOMAINS_PATH
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_domain(domain_id: str, *, domains_path: Path | None = None) -> DomainSpec:
    data = load_domains_yaml(domains_path)
    key = domain_id.strip().lower()
    if key not in data:
        known = ", ".join(sorted(data.keys())) if data else "(vazio)"
        raise KeyError(f"Domínio '{domain_id}' não encontrado em domains.yaml. Conhecidos: {known}")

    block = data[key] or {}
    tables_raw = block.get("tables") or []
    tables = tuple(str(t).strip().upper() for t in tables_raw if str(t).strip())
    label = str(block.get("label") or key).strip()
    desc = str(block.get("description") or "").strip()
    override = block.get("mart_override")
    if override is not None and not isinstance(override, dict):
        override = None
    return DomainSpec(
        domain_id=key,
        label=label,
        tables=tables,
        description=desc,
        mart_override=override,
    )


def resolve_tables_for_run(
    *,
    domain: str | None,
    include_tables: list[str] | None,
    domains_path: Path | None = None,
) -> set[str] | None:
    """
    Retorna conjunto de tabelas Protheus (upper) ou None = sem filtro (todas).
    `include_tables` tem precedência sobre --domain quando ambos presentes.
    """
    if include_tables:
        return {t.strip().upper() for t in include_tables if t.strip()}
    if domain:
        spec = get_domain(domain, domains_path=domains_path)
        return set(spec.tables)
    return None
