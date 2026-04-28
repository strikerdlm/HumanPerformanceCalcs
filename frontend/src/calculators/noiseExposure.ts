/**
 * Noise Exposure & Daily Noise Dose
 *
 * OSHA (29 CFR §1910.95): criterion 90 dBA, exchange rate 5 dB.
 * NIOSH REL (DHHS Pub. No. 98-126): criterion 85 dBA, exchange rate 3 dB.
 *
 * For occupational and industrial-hygiene research/education only — not a
 * legal compliance tool.
 *
 * References:
 *   - OSHA 29 CFR §1910.95 (2023). https://www.osha.gov/laws-regs/regulations/
 *   - NIOSH (1998). DHHS Publication 98-126.
 *   - Suter, A. H. (1991). Noise and its effects.
 */

/**
 * Permissible exposure duration (hours) at a given SPL.
 *
 * T = 8 / 2^((SPL − Lc) / q)
 *
 * @param spl_dba Sound pressure level, dB(A)
 * @param criterion_level Lc — criterion level (default 90 dBA, OSHA)
 * @param exchange_rate q — exchange rate (default 5 dB, OSHA)
 */
export function permissibleDuration(
  spl_dba: number,
  criterion_level: number = 90.0,
  exchange_rate: number = 5.0
): number {
  const exponent = (spl_dba - criterion_level) / exchange_rate;
  return 8.0 / Math.pow(2, exponent);
}

function dosePercent(
  spl_dba: number,
  duration_hours: number,
  criterion_level: number,
  exchange_rate: number
): number {
  const allowed = permissibleDuration(spl_dba, criterion_level, exchange_rate);
  return 100 * (duration_hours / allowed);
}

/**
 * Total OSHA noise dose (%) summed across multiple exposure segments.
 * ≥ 100% exceeds the permissible daily dose.
 */
export function noiseDoseOsha(levels_dba: number[], durations_hours: number[]): number {
  if (levels_dba.length !== durations_hours.length) {
    throw new Error('`levels_dba` and `durations_hours` length mismatch');
  }
  let total = 0;
  for (let i = 0; i < levels_dba.length; i++) {
    total += dosePercent(levels_dba[i], durations_hours[i], 90.0, 5.0);
  }
  return total;
}

/**
 * Total NIOSH REL noise dose (%) — criterion 85 dBA, exchange rate 3 dB.
 */
export function noiseDoseNiosh(levels_dba: number[], durations_hours: number[]): number {
  if (levels_dba.length !== durations_hours.length) {
    throw new Error('`levels_dba` and `durations_hours` length mismatch');
  }
  let total = 0;
  for (let i = 0; i < levels_dba.length; i++) {
    total += dosePercent(levels_dba[i], durations_hours[i], 85.0, 3.0);
  }
  return total;
}
