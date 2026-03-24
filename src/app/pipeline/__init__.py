"""Orquestração do pipeline semântico (SX3 → event log → fluxo → validação)."""
from __future__ import annotations

from app.pipeline.runner import parse_args, run_pipeline

__all__ = ["parse_args", "run_pipeline"]
