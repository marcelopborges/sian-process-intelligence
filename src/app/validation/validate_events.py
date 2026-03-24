"""Validação de candidatos contra regras mart (dbt / staging)."""
from __future__ import annotations

from app.validation.dbt_alignment import classify_event_candidate, load_mart_registry

__all__ = ["classify_event_candidate", "load_mart_registry"]
