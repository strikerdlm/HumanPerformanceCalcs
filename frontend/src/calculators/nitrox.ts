/**
 * Nitrox / mixed-gas dive planning helpers.
 *
 * Standard formulas (NOAA Diving Manual; recreational-/technical-diver
 * conventions). All depths are metric (msw) and pressures are bar/ata
 * absolute. Sea-water depth ↔ pressure assumes 10 m ≈ 1 bar.
 *
 *   MOD          : maximum operating depth where PO2 ≤ PO2_max
 *                  MOD_m = (PO2_max / FO2 − 1) · 10
 *   EAD          : equivalent air depth (nitrogen-equivalent)
 *                  EAD_m = ((1 − FO2) / 0.79) · (D + 10) − 10
 *   Best mix     : FO2 that yields PO2_target at the planned depth
 *                  FO2 = PO2_target / (D/10 + 1)
 *   END (trimix) : equivalent narcotic depth (treats N2 + O2 as narcotic)
 *                  END_m = ((F_N2 + F_O2) / 0.79) · (D + 10) − 10
 *
 * Pairs with the Bühlmann ZH-L16-GF planner in `buhlmann.ts`.
 *
 * SCOPE: educational / planning. Always cross-check with a redundant tool
 * and operational protocols before diving.
 */

function ensurePositive(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

function ensureFraction(name: string, v: number): number {
  if (!Number.isFinite(v) || v < 0 || v > 1) {
    throw new Error(`${name} must be a fraction in [0, 1]`);
  }
  return v;
}

/**
 * Maximum Operating Depth in metres of sea water for a given oxygen
 * fraction and oxygen partial-pressure ceiling.
 *
 * Common PO2_max values:
 *   1.4 ata — recreational working ceiling
 *   1.6 ata — emergency / decompression-only ceiling
 */
export function maxOperatingDepth(args: {
  /** Oxygen fraction in the breathing gas (0–1). */
  fo2: number;
  /** Maximum allowed oxygen partial pressure (ata). */
  po2_max: number;
}): number {
  const fo2 = ensureFraction('fo2', args.fo2);
  if (fo2 === 0) throw new Error('fo2 must be > 0 for MOD calculation');
  const po2 = ensurePositive('po2_max', args.po2_max);
  return (po2 / fo2 - 1) * 10;
}

/**
 * Equivalent Air Depth: depth at which breathing air would yield the same
 * inspired N2 partial pressure as the supplied nitrox at the planned depth.
 * Used to apply standard air decompression tables to nitrox dives.
 */
export function equivalentAirDepth(args: {
  /** Oxygen fraction in the breathing gas (0–1). */
  fo2: number;
  /** Planned depth, msw. */
  depth_m: number;
}): number {
  const fo2 = ensureFraction('fo2', args.fo2);
  if (fo2 >= 1) throw new Error('fo2 must be < 1 for EAD calculation');
  const depth = args.depth_m;
  if (!Number.isFinite(depth) || depth < 0) {
    throw new Error('depth_m must be a finite, non-negative number');
  }
  return ((1 - fo2) / 0.79) * (depth + 10) - 10;
}

/**
 * Best Mix: the oxygen fraction that yields a target PO2 at the planned depth.
 *
 *   FO2 = PO2_target / (D/10 + 1)
 *
 * If the resulting FO2 exceeds 1 the depth is too shallow for the target
 * PO2 and the function returns 1.0 (clamped).
 */
export function bestMix(args: { depth_m: number; po2_target: number }): number {
  const depth = args.depth_m;
  if (!Number.isFinite(depth) || depth < 0) {
    throw new Error('depth_m must be a finite, non-negative number');
  }
  const po2 = ensurePositive('po2_target', args.po2_target);
  const fo2 = po2 / (depth / 10 + 1);
  return Math.min(1.0, Math.max(0.0, fo2));
}

/**
 * Equivalent Narcotic Depth (helium replaces narcotic gas).
 *
 *   END_m = ((F_N2 + F_O2) / 0.79) · (D + 10) − 10
 *
 * Treating O2 as narcotic is a conservative convention adopted by most
 * technical-diving agencies. If you prefer the "O2 not narcotic" model use
 * `endNoOxygenNarcosis`.
 */
export function equivalentNarcoticDepth(args: {
  fo2: number;
  /** Helium fraction (0–1). */
  fhe: number;
  depth_m: number;
}): number {
  const fo2 = ensureFraction('fo2', args.fo2);
  const fhe = ensureFraction('fhe', args.fhe);
  if (fo2 + fhe > 1) throw new Error('fo2 + fhe must not exceed 1');
  const fn2 = 1 - fo2 - fhe;
  const depth = args.depth_m;
  if (!Number.isFinite(depth) || depth < 0) {
    throw new Error('depth_m must be a finite, non-negative number');
  }
  return ((fn2 + fo2) / 0.79) * (depth + 10) - 10;
}

/** END variant treating only N2 as narcotic. */
export function endNoOxygenNarcosis(args: {
  fo2: number;
  fhe: number;
  depth_m: number;
}): number {
  const fo2 = ensureFraction('fo2', args.fo2);
  const fhe = ensureFraction('fhe', args.fhe);
  if (fo2 + fhe > 1) throw new Error('fo2 + fhe must not exceed 1');
  const fn2 = 1 - fo2 - fhe;
  const depth = args.depth_m;
  if (!Number.isFinite(depth) || depth < 0) {
    throw new Error('depth_m must be a finite, non-negative number');
  }
  return (fn2 / 0.79) * (depth + 10) - 10;
}

/**
 * PO2 at depth for a given oxygen fraction.
 *
 *   PO2 = FO2 · (D/10 + 1)
 */
export function po2AtDepth(fo2: number, depth_m: number): number {
  ensureFraction('fo2', fo2);
  if (!Number.isFinite(depth_m) || depth_m < 0) {
    throw new Error('depth_m must be a finite, non-negative number');
  }
  return fo2 * (depth_m / 10 + 1);
}
