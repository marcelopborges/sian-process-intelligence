#!/usr/bin/env python3
"""
Validação offline: lê `sx3_event_candidates.json` e `process_flow.json` em --output
e grava `validation/validation_report.json`.

Uso:
  python scripts/run_validation.py --output data/outputs/sx3_semantic
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _bootstrap import ensure_src_on_path  # noqa: E402

ensure_src_on_path()

from app.validation.validate_sequences import validate_linear_edges  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Validação offline (arestas + resumo dbt).")
    p.add_argument("--output", "-o", type=Path, required=True, help="Diretório com artefatos.")
    args = p.parse_args()
    out = args.output
    cand_path = out / "sx3_event_candidates.json"
    flow_path = out / "process_flow.json"
    if not cand_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {cand_path}")
    with cand_path.open(encoding="utf-8") as f:
        enriched = json.load(f)
    dbt_summary: dict[str, int] = {}
    for e in enriched:
        k = str(e.get("dbt_classification") or "")
        dbt_summary[k] = dbt_summary.get(k, 0) + 1
    edge_issues: list[str] = []
    n_edges = 0
    if flow_path.exists():
        with flow_path.open(encoding="utf-8") as f:
            payload = json.load(f)
        edges = payload.get("edges") or []
        n_edges = len(edges)
        if isinstance(edges, list) and edges and isinstance(edges[0], dict):
            edge_issues = validate_linear_edges(edges)  # type: ignore[arg-type]
    val_dir = out / "validation"
    val_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "candidates_total": len(enriched),
        "dbt_classification_counts": dbt_summary,
        "process_flow_edges": n_edges,
        "linear_edge_issues": edge_issues,
    }
    vpath = val_dir / "validation_report.json"
    with vpath.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"OK: relatório → {vpath}")


if __name__ == "__main__":
    main()
