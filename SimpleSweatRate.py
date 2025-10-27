"""Compatibility wrapper for legacy SimpleSweatRate module.

Exposes sweat-rate related helpers from ``legacy_apps/SimpleSweatRate.py`` at
the package root so that `import SimpleSweatRate` continues to succeed.
"""
from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import TYPE_CHECKING

_LEGACY_PATH = os.path.join(os.path.dirname(__file__), "legacy_apps", "SimpleSweatRate.py")

_spec = importlib.util.spec_from_file_location("_legacy_Sweat", _LEGACY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError("Could not load legacy SimpleSweatRate module from legacy_apps/SimpleSweatRate.py")

_legacy_module: ModuleType = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_legacy_module)  # type: ignore[call-arg]

# Re-export public API expected by the tests ----------------------------------
calculate_sweat_rate = _legacy_module.calculate_sweat_rate  # type: ignore[attr-defined]
get_dehydration_percentage = _legacy_module.get_dehydration_percentage  # type: ignore[attr-defined]
interpret_sweat_rate = _legacy_module.interpret_sweat_rate  # type: ignore[attr-defined]
interpret_dehydration = _legacy_module.interpret_dehydration  # type: ignore[attr-defined]

__all__ = [
    "calculate_sweat_rate",
    "get_dehydration_percentage",
    "interpret_sweat_rate",
    "interpret_dehydration",
]

if TYPE_CHECKING:  # pragma: no cover
    from legacy_apps.SimpleSweatRate import calculate_sweat_rate as calculate_sweat_rate  # noqa: F401, F811
    from legacy_apps.SimpleSweatRate import get_dehydration_percentage as get_dehydration_percentage  # noqa: F401, F811
    from legacy_apps.SimpleSweatRate import interpret_sweat_rate as interpret_sweat_rate  # noqa: F401, F811
    from legacy_apps.SimpleSweatRate import interpret_dehydration as interpret_dehydration  # noqa: F401, F811