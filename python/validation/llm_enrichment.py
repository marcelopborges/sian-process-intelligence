"""
Enriquecimento opcional com LLM (explicação / confiança semântica).

- Não infere joins nem regras de negócio.
- Sem dependência obrigatória: usa urllib (stdlib) se OPENAI_API_KEY estiver definida.
- Sem chave: gera texto explicativo baseado em regras (auditoria sempre preenchida).
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LlmAuditRecord:
    """Metadados de auditoria por candidato (opcional)."""

    used_llm_api: bool
    model: str | None
    prompt_version: str
    raw_response_excerpt: str | None = None
    error: str | None = None


@dataclass
class LlmEnrichmentResult:
    semantic_description: str
    revised_confidence: float | None
    audit: LlmAuditRecord


def _rule_based_description(
    *,
    activity: str,
    source_table: str,
    source_column: str,
    dbt_classification: str,
    justification: str,
) -> str:
    return (
        f"Atividade sugerida: {activity} (tabela {source_table}, campo {source_column}). "
        f"Classificação dbt: {dbt_classification}. {justification}"
    )


def enrich_candidate(
    *,
    activity: str,
    source_table: str,
    source_column: str,
    heuristic_score: float,
    dbt_classification: str,
    justification: str,
    confidence_level: str,
    use_llm: bool,
) -> LlmEnrichmentResult:
    """
    Enriquece um candidato. Se `use_llm` e OPENAI_API_KEY, chama API OpenAI (chat completions).
    Caso contrário, descrição por regras + audit flag.
    """
    audit = LlmAuditRecord(
        used_llm_api=False,
        model=None,
        prompt_version="sx3-event-enrich-v1",
    )
    base_desc = _rule_based_description(
        activity=activity,
        source_table=source_table,
        source_column=source_column,
        dbt_classification=dbt_classification,
        justification=justification,
    )

    if not use_llm:
        return LlmEnrichmentResult(
            semantic_description=base_desc,
            revised_confidence=None,
            audit=audit,
        )

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        audit.error = "OPENAI_API_KEY não definida; usando descrição por regras."
        logger.warning(audit.error)
        return LlmEnrichmentResult(
            semantic_description=base_desc,
            revised_confidence=None,
            audit=audit,
        )

    system = (
        "Você é um especialista em Protheus (TOTVS) e process mining. "
        "Responda apenas JSON com chaves: semantic_description (string), "
        "revised_confidence (float 0-1 opcional). "
        "Não invente joins SQL nem regras de processo; apenas interprete o candidato."
    )
    user = json.dumps(
        {
            "activity": activity,
            "source_table": source_table,
            "source_column": source_column,
            "heuristic_score": heuristic_score,
            "dbt_classification": dbt_classification,
            "confidence_level": confidence_level,
            "notes": justification,
        },
        ensure_ascii=False,
    )

    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }

    try:
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"].strip()
        parsed: dict[str, Any] = {}
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Modelo pode envolver JSON em ```json ... ```
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(content[start : end + 1])
                except json.JSONDecodeError:
                    parsed = {}
        desc = parsed.get("semantic_description") or content or base_desc
        rev = parsed.get("revised_confidence")
        rev_f = float(rev) if rev is not None else None
        audit.used_llm_api = True
        audit.model = payload["model"]
        audit.raw_response_excerpt = content[:2000]
        return LlmEnrichmentResult(
            semantic_description=desc,
            revised_confidence=rev_f,
            audit=audit,
        )
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, ValueError) as e:
        audit.error = str(e)
        logger.warning("Falha no enriquecimento LLM: %s", e)
        return LlmEnrichmentResult(
            semantic_description=base_desc,
            revised_confidence=None,
            audit=audit,
        )


def audit_dict(audit: LlmAuditRecord) -> dict[str, Any]:
    return {
        "used_llm_api": audit.used_llm_api,
        "model": audit.model,
        "prompt_version": audit.prompt_version,
        "raw_response_excerpt": audit.raw_response_excerpt,
        "error": audit.error,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
