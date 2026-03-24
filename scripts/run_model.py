#!/usr/bin/env python3
"""Camada MODEL: candidatos → agregação em event log candidato."""
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
    if "--build-event-log" not in argv:
        argv = ["--build-event-log", *argv]
    raise SystemExit(run_pipeline(argv))


if __name__ == "__main__":
    main()
