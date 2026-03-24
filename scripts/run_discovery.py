#!/usr/bin/env python3
"""Apenas descoberta: candidatos SX3 + DuckDB (sem event log nem fluxo)."""
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
    raise SystemExit(run_pipeline(sys.argv[1:]))


if __name__ == "__main__":
    main()
