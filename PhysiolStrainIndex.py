"""Compatibility wrapper for legacy Physiological Strain Index module.

This shim allows importing ``PhysiolStrainIndex`` from the repository root,
re-exporting the functions required by the test-suite without duplicating
implementation code.
"""
from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import TYPE_CHECKING

_LEGACY_PATH = os.path.join(os.path.dirname(__file__), "legacy_apps", "PhysiolStrainIndex.py")

_spec = importlib.util.spec_from_file_location("_legacy_PSI", _LEGACY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError("Could not load legacy PhysiolStrainIndex module from legacy_apps/PhysiolStrainIndex.py")

_legacy_module: ModuleType = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_legacy_module)  # type: ignore[call-arg]

# Re-export functions expected by tests ---------------------------------------
physiological_strain_index = _legacy_module.physiological_strain_index  # type: ignore[attr-defined]
interpret_psi = _legacy_module.interpret_psi                                # type: ignore[attr-defined]

__all__ = [
    "physiological_strain_index",
    "interpret_psi",
]

# Typing helpers --------------------------------------------------------------
if TYPE_CHECKING:  # pragma: no cover
    from legacy_apps.PhysiolStrainIndex import physiological_strain_index as physiological_strain_index  # noqa: F401, F811
    from legacy_apps.PhysiolStrainIndex import interpret_psi as interpret_psi  # noqa: F401, F811