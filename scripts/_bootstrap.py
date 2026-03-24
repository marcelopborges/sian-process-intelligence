"""Garante `src/` no sys.path ao rodar scripts sem `pip install -e .`."""
from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def ensure_src_on_path() -> Path:
    root = repo_root()
    src = root / "src"
    s = str(src)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root
