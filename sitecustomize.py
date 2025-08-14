import os
import sys

# Automatically add the legacy_apps directory to Python's module search path so
# that legacy calculators (e.g., WCT.py, PhysiolStrainIndex.py, SimpleSweatRate.py)
# can be imported without needing to modify tests or user code.
# This file is automatically imported by Python when present on the search path
# (see the standard library's `site` module behaviour).

legacy_dir = os.path.join(os.path.dirname(__file__), "legacy_apps")
if os.path.isdir(legacy_dir) and legacy_dir not in sys.path:
    # Prepend to ensure it has priority over similarly named modules elsewhere
    sys.path.insert(0, legacy_dir)