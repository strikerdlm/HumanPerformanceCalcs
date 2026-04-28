/**
 * Bounded parameter-sweep helpers for the Predicted Heat Strain (PHS) model.
 *
 * Wraps `predictedHeatStrain` (from `heatStress.ts`) to produce 1-D and 2-D
 * grids of a chosen metric while holding the remaining inputs constant.
 *
 * Mirrors `calculators/simulation.py` (sweep_phs_metric_1d / sweep_phs_metric_2d).
 */

import { predictedHeatStrain } from './heatStress';

export type PHSSweepParameter =
  | 'metabolic_rate_w_m2'
  | 'air_temperature_C'
  | 'mean_radiant_temperature_C'
  | 'relative_humidity_percent'
  | 'air_velocity_m_s'
  | 'clothing_insulation_clo';

export type PHSSweepMetric =
  | 'allowable_exposure_minutes'
  | 'core_temperature_C_at_horizon'
  | 'dehydration_percent_body_mass_at_horizon';

export interface PHSSweep1DResult {
  parameter_name: PHSSweepParameter;
  parameter_unit: string;
  parameter_values: number[];
  metric_name: PHSSweepMetric;
  metric_unit: string;
  metric_values: number[];
}

export interface PHSSweep2DResult {
  x_name: PHSSweepParameter;
  x_unit: string;
  x_values: number[];
  y_name: PHSSweepParameter;
  y_unit: string;
  y_values: number[];
  metric_name: PHSSweepMetric;
  metric_unit: string;
  z_values: number[][]; // shape: [y_values.length][x_values.length]
}

const PHS_PARAMETER_UNITS: Record<PHSSweepParameter, string> = {
  metabolic_rate_w_m2: 'W/m²',
  air_temperature_C: '°C',
  mean_radiant_temperature_C: '°C',
  relative_humidity_percent: '%',
  air_velocity_m_s: 'm/s',
  clothing_insulation_clo: 'clo',
};

const PHS_METRIC_UNITS: Record<PHSSweepMetric, string> = {
  allowable_exposure_minutes: 'min',
  core_temperature_C_at_horizon: '°C',
  dehydration_percent_body_mass_at_horizon: '% body mass',
};

export interface PHSScenario {
  exposure_minutes: number;
  metabolic_rate_w_m2: number;
  air_temperature_C: number;
  mean_radiant_temperature_C: number;
  relative_humidity_percent: number;
  air_velocity_m_s: number;
  clothing_insulation_clo: number;
  mechanical_power_w_m2?: number;
  body_mass_kg?: number;
  body_surface_area_m2?: number;
  baseline_core_temp_C?: number;
  core_temp_limit_C?: number;
  dehydration_limit_percent?: number;
}

function evaluateMetric(scenario: PHSScenario, metric: PHSSweepMetric): number {
  const result = predictedHeatStrain(
    scenario.metabolic_rate_w_m2,
    scenario.air_temperature_C,
    scenario.mean_radiant_temperature_C,
    scenario.relative_humidity_percent,
    scenario.air_velocity_m_s,
    scenario.clothing_insulation_clo,
    scenario.exposure_minutes,
    scenario.mechanical_power_w_m2 ?? 0,
    scenario.body_mass_kg ?? 75,
    scenario.body_surface_area_m2 ?? 1.9,
    scenario.baseline_core_temp_C ?? 37.0,
    scenario.core_temp_limit_C ?? 38.5,
    scenario.dehydration_limit_percent ?? 5.0
  );
  switch (metric) {
    case 'allowable_exposure_minutes':
      return result.allowableExposure_min;
    case 'core_temperature_C_at_horizon':
      return result.predictedCoreTemp_C;
    case 'dehydration_percent_body_mass_at_horizon':
      return result.dehydrationPercent;
  }
}

function linspace(a: number, b: number, n: number): number[] {
  if (n < 2) throw new Error('linspace requires n >= 2');
  if (n === 2) return [a, b];
  const step = (b - a) / (n - 1);
  const out: number[] = [];
  for (let i = 0; i < n; i++) out.push(a + i * step);
  return out;
}

/**
 * Sweep one PHS input parameter and compute a chosen metric per value.
 */
export function sweepPhsMetric1d(args: {
  sweep_parameter: PHSSweepParameter;
  start: number;
  stop: number;
  n_points: number;
  metric: PHSSweepMetric;
  scenario: PHSScenario;
  max_evaluations?: number;
}): PHSSweep1DResult {
  if (!(args.sweep_parameter in PHS_PARAMETER_UNITS)) {
    throw new Error(`Unsupported sweep_parameter: ${args.sweep_parameter}`);
  }
  if (!(args.metric in PHS_METRIC_UNITS)) {
    throw new Error(`Unsupported metric: ${args.metric}`);
  }
  if (!Number.isInteger(args.n_points) || args.n_points < 2 || args.n_points > 2000) {
    throw new Error('n_points must be an integer between 2 and 2000');
  }
  if (args.scenario.exposure_minutes <= 0) {
    throw new Error('exposure_minutes must be > 0');
  }
  const maxEval = args.max_evaluations ?? 2500;
  if (args.n_points > maxEval) {
    throw new Error('Requested sweep exceeds max_evaluations');
  }
  if (!Number.isFinite(args.start) || !Number.isFinite(args.stop)) {
    throw new Error('start/stop must be finite');
  }

  const xs = linspace(args.start, args.stop, args.n_points);
  const ys: number[] = [];
  for (const x of xs) {
    const scen: PHSScenario = { ...args.scenario, [args.sweep_parameter]: x };
    ys.push(evaluateMetric(scen, args.metric));
  }

  return {
    parameter_name: args.sweep_parameter,
    parameter_unit: PHS_PARAMETER_UNITS[args.sweep_parameter],
    parameter_values: xs,
    metric_name: args.metric,
    metric_unit: PHS_METRIC_UNITS[args.metric],
    metric_values: ys,
  };
}

/**
 * Sweep two PHS input parameters and compute a chosen metric over the grid.
 *
 * z_values is a 2-D array of shape [y_values.length][x_values.length].
 */
export function sweepPhsMetric2d(args: {
  x_parameter: PHSSweepParameter;
  x_start: number;
  x_stop: number;
  x_points: number;
  y_parameter: PHSSweepParameter;
  y_start: number;
  y_stop: number;
  y_points: number;
  metric: PHSSweepMetric;
  scenario: PHSScenario;
  max_evaluations?: number;
}): PHSSweep2DResult {
  if (!(args.x_parameter in PHS_PARAMETER_UNITS)) {
    throw new Error(`Unsupported x_parameter: ${args.x_parameter}`);
  }
  if (!(args.y_parameter in PHS_PARAMETER_UNITS)) {
    throw new Error(`Unsupported y_parameter: ${args.y_parameter}`);
  }
  if (args.x_parameter === args.y_parameter) {
    throw new Error('x_parameter and y_parameter must be different');
  }
  if (!(args.metric in PHS_METRIC_UNITS)) {
    throw new Error(`Unsupported metric: ${args.metric}`);
  }
  if (
    !Number.isInteger(args.x_points) ||
    !Number.isInteger(args.y_points) ||
    args.x_points < 2 ||
    args.x_points > 500 ||
    args.y_points < 2 ||
    args.y_points > 500
  ) {
    throw new Error('x_points/y_points must be integers between 2 and 500');
  }
  if (args.scenario.exposure_minutes <= 0) {
    throw new Error('exposure_minutes must be > 0');
  }
  const maxEval = args.max_evaluations ?? 2500;
  if (args.x_points * args.y_points > maxEval) {
    throw new Error('Requested grid exceeds max_evaluations');
  }
  if (
    !Number.isFinite(args.x_start) ||
    !Number.isFinite(args.x_stop) ||
    !Number.isFinite(args.y_start) ||
    !Number.isFinite(args.y_stop)
  ) {
    throw new Error('start/stop must be finite');
  }

  const xs = linspace(args.x_start, args.x_stop, args.x_points);
  const ys = linspace(args.y_start, args.y_stop, args.y_points);
  const z: number[][] = [];

  for (const y of ys) {
    const row: number[] = [];
    for (const x of xs) {
      const scen: PHSScenario = {
        ...args.scenario,
        [args.x_parameter]: x,
        [args.y_parameter]: y,
      };
      row.push(evaluateMetric(scen, args.metric));
    }
    z.push(row);
  }

  return {
    x_name: args.x_parameter,
    x_unit: PHS_PARAMETER_UNITS[args.x_parameter],
    x_values: xs,
    y_name: args.y_parameter,
    y_unit: PHS_PARAMETER_UNITS[args.y_parameter],
    y_values: ys,
    metric_name: args.metric,
    metric_unit: PHS_METRIC_UNITS[args.metric],
    z_values: z,
  };
}
