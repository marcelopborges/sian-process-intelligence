#!/usr/bin/env python3
"""
Inferência de candidatos a eventos (SX3 + DuckDB).

**Preferência:** `python scripts/run_pipeline.py` ou `python -m app.pipeline.runner`.

Este script mantém compatibilidade com chamadas antigas (`python scripts/infer_events_from_sx3.py`).
"""
from __future__ import annotations

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _bootstrap import ensure_src_on_path  # noqa: E402

ensure_src_on_path()

from app.pipeline.runner import main  # noqa: E402

if __name__ == "__main__":
    main()
