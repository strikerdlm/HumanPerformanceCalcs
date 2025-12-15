"""Motion sickness (MSSQ-short) — CLI wrapper.

This is a thin wrapper around the deterministic `calculators.mssq` implementation.
It exists primarily to satisfy the `aerospace_medicine.motion_sickness` package structure
documented in `docs/PROJECT_STRUCTURE.md`.

For interactive use, prefer the Streamlit UI:
- streamlit run streamlit_app.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence

from calculators.mssq import MSSQ_SHORT_ITEMS, MssqShortInputs, compute_mssq_short


def _parse_scores(arg: str) -> tuple[int, ...]:
    parts = [p.strip() for p in arg.split(",") if p.strip() != ""]
    if len(parts) != 9:
        raise ValueError("Expected 9 comma-separated integers for a section (0..3).")
    out: list[int] = []
    for i, p in enumerate(parts):
        try:
            v = int(p)
        except ValueError as e:
            raise ValueError(f"Invalid integer at position {i+1}: {p!r}") from e
        out.append(v)
    return tuple(out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MSSQ-short calculator (deterministic).")
    parser.add_argument(
        "--section-a",
        required=True,
        help="9 comma-separated integers (0..3) for Section A, in the order of MSSQ_SHORT_ITEMS.",
    )
    parser.add_argument(
        "--section-b",
        required=True,
        help="9 comma-separated integers (0..3) for Section B, in the order of MSSQ_SHORT_ITEMS.",
    )
    args = parser.parse_args(argv)

    a = _parse_scores(str(args.section_a))
    b = _parse_scores(str(args.section_b))

    res = compute_mssq_short(MssqShortInputs(section_a_scores_0_3=a, section_b_scores_0_3=b))
    print("MSSQ-short (raw)")
    print("Items order:")
    for i, name in enumerate(MSSQ_SHORT_ITEMS, start=1):
        print(f"  {i}. {name}")
    print("")
    print(f"Section A (0–27): {res.section_a_sum_0_27}")
    print(f"Section B (0–27): {res.section_b_sum_0_27}")
    print(f"Total (0–54):     {res.total_sum_0_54}")
    print(f"Rivera 2022 quartile band: {res.rivera_2022_percentile_band}")
    return 0


if __name__ == \"__main__\":
    raise SystemExit(main())


