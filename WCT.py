"""Compatibility wrapper for legacy WCT module.

This file makes the `wind_chill_temperature` and `interpret_wind_chill` functions
available as top-level imports (`import WCT`) so that existing unit tests and
external user code that rely on this import path continue to work.
The implementation is lazily loaded from ``legacy_apps/WCT.py`` to avoid code
duplication and to ensure that any updates to the legacy module are picked up
without modification here.
"""
from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import TYPE_CHECKING

_LEGACY_PATH = os.path.join(os.path.dirname(__file__), "legacy_apps", "WCT.py")

_spec = importlib.util.spec_from_file_location("_legacy_WCT", _LEGACY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover – defensive
    raise ImportError("Could not load legacy WCT module from legacy_apps/WCT.py")

_legacy_module: ModuleType = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_legacy_module)  # type: ignore[call-arg]

# Re-export public API expected by the test-suite -----------------------------
wind_chill_temperature = _legacy_module.wind_chill_temperature  # type: ignore[attr-defined]
interpret_wind_chill = _legacy_module.interpret_wind_chill      # type: ignore[attr-defined]

__all__ = [
    "wind_chill_temperature",
    "interpret_wind_chill",
]

# Help static analysers / IDEs ------------------------------------------------
if TYPE_CHECKING:  # pragma: no cover
    from legacy_apps.WCT import wind_chill_temperature as wind_chill_temperature  # noqa: F811
    from legacy_apps.WCT import interpret_wind_chill as interpret_wind_chill      # noqa: F811