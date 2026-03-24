#!/usr/bin/env python3
"""Entrypoint: inferência de relacionamentos SX3 → `app.discovery.relationship_runner`."""
from __future__ import annotations

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))

from _bootstrap import ensure_src_on_path  # noqa: E402

ensure_src_on_path()

from app.discovery.relationship_runner import main  # noqa: E402

if __name__ == "__main__":
    main()
