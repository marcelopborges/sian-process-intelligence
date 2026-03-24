"""Inferência de candidatos a eventos a partir de metadados SX3 + DuckDB staging."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.discovery.heuristics import EXPECTED_TABLE, KEYWORD_MAP


@dataclass(frozen=True)
class EventCandidateRaw:
    candidate_id: str
    activity: str
    source_table: str
    source_column: str
    confidence: float
    reason: str
    created_at_utc: str


def _contains_any_keywords(haystack: str, keywords: list[str]) -> bool:
    up = haystack.upper()
    return any(k in up for k in keywords)


def infer_event_candidates(
    *,
    sx3_meta: dict[str, dict[str, Any]],
    duckdb_columns_by_table: dict[str, set[str]],
    allowed_tables: set[str] | None = None,
) -> list[EventCandidateRaw]:
    now = datetime.now(UTC).isoformat()
    out: list[EventCandidateRaw] = []

    def add(activity: str, table: str, column: str, confidence: float, reason: str) -> None:
        if allowed_tables is not None and table.upper() not in allowed_tables:
            return
        out.append(
            EventCandidateRaw(
                candidate_id=f"{activity}:{table}.{column}:{len(out)}",
                activity=activity,
                source_table=table,
                source_column=column,
                confidence=float(confidence),
                reason=reason,
                created_at_utc=now,
            )
        )

    for table, fields in sx3_meta.items():
        if allowed_tables is not None and table.upper() not in allowed_tables:
            continue
        for col, meta in fields.items():
            titulo = getattr(meta, "titulo", None) or ""
            desc = getattr(meta, "desc", None) or ""
            desc_eng = getattr(meta, "desc_eng", None) or ""
            combined = f"{titulo} {desc} {desc_eng}".strip()
            if not combined:
                continue
            for activity, kws in KEYWORD_MAP.items():
                if activity == "EVENTO_FINANCEIRO_GERADO":
                    continue
                if _contains_any_keywords(combined, kws):
                    boost = (
                        0.15 if re.search(r"\bDT\b|DATA", (titulo + " " + desc).upper()) else 0.0
                    )
                    expected_boost = 0.20 if EXPECTED_TABLE.get(activity) == table else 0.0
                    confidence = min(1.0, 0.45 + boost + expected_boost)
                    add(
                        activity,
                        table,
                        col,
                        confidence=confidence,
                        reason="keyword_match:"
                        + kws[0]
                        + (
                            f";expected_table_boost:{expected_boost:.2f}" if expected_boost else ""
                        ),
                    )
                    break

    fk7_cols = duckdb_columns_by_table.get("FK7", set())
    tech_col = "F7_DBALTERACAO" if "F7_DBALTERACAO" in fk7_cols else None
    if tech_col is None and "DBALTERACAO" in fk7_cols:
        tech_col = "DBALTERACAO"
    if tech_col:
        add(
            "EVENTO_FINANCEIRO_GERADO",
            "FK7",
            tech_col,
            confidence=0.30,
            reason=(
                f"tech_ts_match:FK7.{tech_col} (atividade também depende de F7_COD_EVENTO no mart)"
            ),
        )

    return out


def apply_min_score(candidates: list[EventCandidateRaw], min_score: float) -> list[EventCandidateRaw]:
    return [c for c in candidates if c.confidence >= min_score]


def apply_top_n_per_table(
    candidates: list[EventCandidateRaw],
    top_n: int | None,
) -> list[EventCandidateRaw]:
    if top_n is None or top_n <= 0:
        return candidates
    by_table: dict[str, list[EventCandidateRaw]] = defaultdict(list)
    for c in candidates:
        by_table[c.source_table.upper()].append(c)
    out: list[EventCandidateRaw] = []
    for tbl in sorted(by_table.keys()):
        rows = sorted(by_table[tbl], key=lambda x: -x.confidence)[:top_n]
        out.extend(rows)
    return out
