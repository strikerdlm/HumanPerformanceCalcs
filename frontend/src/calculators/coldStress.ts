/**
 * Cold-exposure physiology calculators.
 *
 * Currently exposes the peak shivering intensity prediction.
 */

/**
 * Predict peak shivering intensity (mL O₂·kg⁻¹·min⁻¹).
 *
 * Shiv_peak = 30.5 + 0.348·VO₂max − 0.909·BMI − 0.233·Age
 *
 * @param vo2max_mlkgmin VO₂max (mL O₂·kg⁻¹·min⁻¹)
 * @param bmi Body Mass Index (kg/m²)
 * @param age_years Age in years
 */
export function peakShiveringIntensity(
  vo2max_mlkgmin: number,
  bmi: number,
  age_years: number
): number {
  return (
    30.5 +
    0.348 * Number(vo2max_mlkgmin) -
    0.909 * Number(bmi) -
    0.233 * Number(age_years)
  );
}
