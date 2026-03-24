#!/usr/bin/env python3
"""
Pipeline completo (padrão): inferência → event log → fluxo → validação.

Sem argumentos, equivale a:
  --build-event-log --build-process-flow --validate

Com argumentos, repassa ao runner (ex.: `--domain cp --output data/outputs/sx3_semantic`).
"""
from __future__ import annotations

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _bootstrap import ensure_src_on_path  # noqa: E402

ensure_src_on_path()

from app.pipeline.runner import run_pipeline  # noqa: E402


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        argv = ["--build-event-log", "--build-process-flow", "--validate"]
    raise SystemExit(run_pipeline(argv))


if __name__ == "__main__":
    main()
