from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.discovery.sx3_loader import Sx3FieldMeta

_TOKEN_SYNONYMS = {
    # Conjunto mínimo para Contas a Pagar; pode evoluir.
    "PREFIXO": "PREFIX",
    "PARCELA": "PARCEL",
    "FORNECE": "CLIFOR",
    "CLIFOR": "CLIFOR",
}


def _token_from_column(col: str) -> str | None:
    """
    Extrai token semântico de um nome de coluna Protheus.
    Ex.: FK7_PREFIX -> PREFIX, e2_prefixo -> PREFIXO
    """
    if not col:
        return None
    s = str(col).strip().upper()
    if "_" not in s:
        return None
    # remove o prefixo (antes do primeiro underscore): E2_, FK7_, FK2_, etc.
    token = s.split("_", 1)[1]
    # remove possíveis sufixos adicionais de moeda/valor para evitar falso positivo
    token = re.sub(r"_(VALOR|DATA|DATA|MOEDA)$", "", token)
    token = _TOKEN_SYNONYMS.get(token, token)
    return token


def _keywords(meta: Sx3FieldMeta | None) -> set[str]:
    if meta is None:
        return set()
    parts = [meta.titulo, meta.desc, meta.desc_eng]
    kws: set[str] = set()
    for p in parts:
        if not p:
            continue
        txt = re.sub(r"[^A-Z0-9ÁÀÂÃÉÊÍÓÔÕÚÇ ]", " ", p.upper())
        for w in txt.split():
            if len(w) >= 4:
                kws.add(w)
    return kws


def _keyword_overlap(a: Sx3FieldMeta | None, b: Sx3FieldMeta | None) -> float:
    ak = _keywords(a)
    bk = _keywords(b)
    if not ak or not bk:
        return 0.0
    inter = ak & bk
    return len(inter) / max(len(ak | bk), 1)


@dataclass(frozen=True)
class RelationshipSuggestion:
    suggestion_id: str
    source_table: str
    target_table: str
    source_column: str
    target_column: str
    confidence: float
    reason: str
    sx3_source_f3: str | None
    sx3_target_f3: str | None
    created_at_utc: str


def infer_relationship_suggestions(
    *,
    sx3_meta: dict[str, dict[str, Sx3FieldMeta]],
    duckdb_tables: list[tuple[str, list[str]]],
) -> list[RelationshipSuggestion]:
    """
    Inferência heurística (sem LLM) para sugestões de relacionamento.

    Heurísticas:
    1) token do nome da coluna coincide (após normalização)
    2) descrições/títulos SX3 têm sobreposição de keywords
    3) (boost) X3_F3 aponta para a tabela alvo
    """
    suggestions: list[RelationshipSuggestion] = []

    # Normaliza tabela (stg_se2 -> SE2)
    def norm_table(t: str) -> str:
        s = t.strip()
        if s.lower().startswith("stg_"):
            s = s[4:]
        return s.upper()

    for i in range(len(duckdb_tables)):
        src_table, src_cols = duckdb_tables[i]
        src_t = norm_table(src_table)
        if src_t not in sx3_meta:
            continue

        for j in range(i + 1, len(duckdb_tables)):
            dst_table, dst_cols = duckdb_tables[j]
            dst_t = norm_table(dst_table)
            if dst_t not in sx3_meta:
                continue

            # Carrega meta por campo para acelerar
            src_meta_fields = sx3_meta.get(src_t, {})
            dst_meta_fields = sx3_meta.get(dst_t, {})

            for src_col in src_cols:
                src_token = _token_from_column(src_col)
                if not src_token:
                    continue
                src_field_meta = src_meta_fields.get(str(src_col).upper())
                src_f3 = src_field_meta.f3 if src_field_meta else None

                for dst_col in dst_cols:
                    dst_token = _token_from_column(dst_col)
                    if not dst_token:
                        continue
                    if dst_token != src_token:
                        continue

                    dst_field_meta = dst_meta_fields.get(str(dst_col).upper())
                    dst_f3 = dst_field_meta.f3 if dst_field_meta else None

                    kw = _keyword_overlap(src_field_meta, dst_field_meta)

                    # Boost por referência explícita via X3_F3
                    boost_ref = 0.0
                    if src_f3 and str(src_f3).upper() == dst_t:
                        boost_ref = 0.2
                    if dst_f3 and str(dst_f3).upper() == src_t:
                        boost_ref = max(boost_ref, 0.2)

                    # Token match é o principal; keywords refinam
                    # Confidence base: 0.55 (token) + 0.35*kw + boost
                    confidence = 0.55 + 0.35 * kw + boost_ref
                    confidence = float(min(max(confidence, 0.0), 1.0))

                    if confidence < 0.6:
                        continue

                    reason_parts = ["token_match"]
                    if kw >= 0.08:
                        reason_parts.append(f"keyword_overlap={kw:.3f}")
                    if boost_ref > 0.0:
                        reason_parts.append(f"X3_F3_ref={boost_ref:.2f}")

                    suggestions.append(
                        RelationshipSuggestion(
                            suggestion_id=str(uuid.uuid4()),
                            source_table=src_t,
                            target_table=dst_t,
                            source_column=str(src_col).upper(),
                            target_column=str(dst_col).upper(),
                            confidence=confidence,
                            reason=";".join(reason_parts),
                            sx3_source_f3=str(src_f3) if src_f3 else None,
                            sx3_target_f3=str(dst_f3) if dst_f3 else None,
                            created_at_utc=datetime.now(UTC).isoformat(),
                        )
                    )

    return suggestions

