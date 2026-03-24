"""Enriquecimento de candidatos com alinhamento dbt, column_role e LLM opcional."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.model.classify_columns import classify_column_role
from app.model.llm_enrichment import audit_dict, enrich_candidate
from app.validation.dbt_alignment import classify_event_candidate, load_mart_registry


@dataclass
class EventCandidateEnriched:
    candidate_id: str
    activity: str
    event_type_suggested: str
    source_table: str
    source_column: str
    column_role: str
    heuristic_score: float
    reason: str
    dbt_classification: str
    justification: str
    confidence_level: str
    semantic_description: str
    llm_revised_confidence: float | None
    llm_audit: dict[str, Any] | None
    created_at_utc: str


def build_enriched_records(
    raw_list: list[Any],
    duckdb_columns_by_table: dict[str, set[str]],
    mart_domain: str | None,
    domains_yaml: Path | None,
    use_llm: bool,
) -> list[EventCandidateEnriched]:
    mart = load_mart_registry(domain=mart_domain or "cp", domains_yaml_path=domains_yaml)
    enriched: list[EventCandidateEnriched] = []
    for raw in raw_list:
        cls, just, conf_level = classify_event_candidate(
            activity=raw.activity,
            source_table=raw.source_table,
            source_column=raw.source_column,
            duckdb_columns_by_table=duckdb_columns_by_table,
            mart=mart,
        )
        role = classify_column_role(raw.source_column)
        llm = enrich_candidate(
            activity=raw.activity,
            source_table=raw.source_table,
            source_column=raw.source_column,
            heuristic_score=raw.confidence,
            dbt_classification=cls,
            justification=just,
            confidence_level=conf_level,
            use_llm=use_llm,
        )
        audit = audit_dict(llm.audit) if use_llm else None
        enriched.append(
            EventCandidateEnriched(
                candidate_id=raw.candidate_id,
                activity=raw.activity,
                event_type_suggested=raw.activity,
                source_table=raw.source_table,
                source_column=raw.source_column,
                column_role=role,
                heuristic_score=raw.confidence,
                reason=raw.reason,
                dbt_classification=cls,
                justification=just,
                confidence_level=conf_level,
                semantic_description=llm.semantic_description,
                llm_revised_confidence=llm.revised_confidence,
                llm_audit=audit,
                created_at_utc=raw.created_at_utc,
            )
        )
    return enriched
