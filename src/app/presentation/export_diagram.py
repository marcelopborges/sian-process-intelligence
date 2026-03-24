"""Exporta artefatos de diagrama (JSON, Markdown) e carrega inputs padronizados."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.process.build_flow import ProcessFlowPayload, payload_to_json_dict


def write_process_flow_artifacts(
    payload: ProcessFlowPayload,
    out_dir: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jpath = out_dir / "process_flow.json"
    mpath = out_dir / "process_flow.md"
    with jpath.open("w", encoding="utf-8") as f:
        json.dump(payload_to_json_dict(payload), f, ensure_ascii=False, indent=2)
    with mpath.open("w", encoding="utf-8") as f:
        f.write("# Fluxo de processo (CP) — candidato SX3\n\n")
        f.write("Gerado automaticamente. Ordenação alinhada a `cp_event_order` (dbt).\n\n")
        f.write("```mermaid\n")
        f.write(payload.mermaid)
        f.write("\n```\n")
    return jpath, mpath


def load_event_log_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("event_log_candidates.json deve ser uma lista JSON.")
    return data


def load_sx3_candidates_json(path: Path | None) -> list[dict[str, Any]] | None:
    if path is None or not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return None


def load_process_flow_json(path: Path) -> dict[str, Any]:
    """Carrega `process_flow.json` (payload serializado pelo pipeline)."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("process_flow.json deve ser um objeto JSON.")
    return data
