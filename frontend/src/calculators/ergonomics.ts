/**
 * Ergonomic postural-assessment scoring — REBA and RULA.
 *
 *   REBA (Rapid Entire Body Assessment) — Hignett & McAtamney (2000)
 *   RULA (Rapid Upper Limb Assessment) — McAtamney & Corlett (1993)
 *
 * Both implementations follow the original published algorithms, including
 * the Group A / Group B sub-scores, the Table A / Table B / Table C
 * lookups, and the load/coupling/muscle-use modifiers. They are intended as
 * deterministic helpers for trained ergonomists; the published algorithms
 * do not replace expert judgment or video-based assessment.
 *
 * References:
 *   Hignett S., McAtamney L. (2000). Rapid Entire Body Assessment (REBA).
 *     Appl. Ergon. 31:201–205. https://doi.org/10.1016/S0003-6870(99)00039-3
 *   McAtamney L., Corlett E.N. (1993). RULA: a survey method for the
 *     investigation of work-related upper limb disorders. Appl. Ergon.
 *     24:91–99. https://doi.org/10.1016/0003-6870(93)90080-S
 */

// ─── REBA ──────────────────────────────────────────────────────────────

export type RebaTrunkPosition =
  | 'upright'
  | 'flex_0_20_or_extend'
  | 'flex_20_60_or_extend_gt_20'
  | 'flex_gt_60';

export type RebaNeckPosition = 'flex_0_20' | 'flex_gt_20_or_extend';

export type RebaLegPosition = 'bilateral_walking_sitting' | 'unilateral_unstable';

export type RebaUpperArm =
  | 'extend_20_to_flex_20'
  | 'extend_gt_20_or_flex_20_45'
  | 'flex_45_90'
  | 'flex_gt_90';

export type RebaLowerArm = 'flex_60_100' | 'flex_lt_60_or_gt_100';

export type RebaWrist = 'flex_or_extend_0_15' | 'flex_or_extend_gt_15';

export type RebaCoupling = 'good' | 'fair' | 'poor' | 'unacceptable';

export interface RebaInputs {
  trunk: RebaTrunkPosition;
  trunk_twist_or_sidebend?: boolean;
  neck: RebaNeckPosition;
  neck_twist_or_sidebend?: boolean;
  legs: RebaLegPosition;
  /** Knee flexion 30–60° (+1) or >60° not sitting (+2). */
  knee_flexion_30_60?: boolean;
  knee_flexion_gt_60_not_sitting?: boolean;

  upper_arm: RebaUpperArm;
  shoulder_raised?: boolean;
  arm_abducted?: boolean;
  arm_supported_or_leaning?: boolean;
  lower_arm: RebaLowerArm;
  wrist: RebaWrist;
  wrist_twisted_or_deviated?: boolean;

  /** Load handled: <5 kg = 0, 5–10 kg = 1, >10 kg = 2. */
  load_score: 0 | 1 | 2;
  /** Shock or sudden buildup of force adds +1. */
  shock_force?: boolean;
  coupling: RebaCoupling;

  /** ≥1 body part held static >1 minute. */
  static_posture_gt_1min?: boolean;
  /** Repeated small-range actions >4/min. */
  repeated_actions_gt_4_per_min?: boolean;
  /** Rapid large changes in posture or unstable base. */
  rapid_or_unstable_actions?: boolean;
}

export interface RebaResult {
  reba_score: number;
  score_a: number;
  score_b: number;
  table_c: number;
  activity_score: number;
  risk_level: 'negligible' | 'low' | 'medium' | 'high' | 'very_high';
  recommended_action: string;
}

const REBA_TRUNK: Record<RebaTrunkPosition, number> = {
  upright: 1,
  flex_0_20_or_extend: 2,
  flex_20_60_or_extend_gt_20: 3,
  flex_gt_60: 4,
};

const REBA_NECK: Record<RebaNeckPosition, number> = {
  flex_0_20: 1,
  flex_gt_20_or_extend: 2,
};

const REBA_LEGS: Record<RebaLegPosition, number> = {
  bilateral_walking_sitting: 1,
  unilateral_unstable: 2,
};

// REBA Table A — Trunk (1..5) × Neck (1..3) × Legs (1..4) → 1..9
// Source: Hignett & McAtamney (2000) Table A.
// Indexed [trunk-1][neck-1][legs-1].
const REBA_TABLE_A: ReadonlyArray<ReadonlyArray<ReadonlyArray<number>>> = [
  // trunk = 1
  [
    [1, 2, 3, 4],
    [1, 2, 3, 4],
    [3, 3, 5, 6],
  ],
  // trunk = 2
  [
    [2, 3, 4, 5],
    [3, 4, 5, 6],
    [4, 5, 6, 7],
  ],
  // trunk = 3
  [
    [2, 4, 5, 6],
    [4, 5, 6, 7],
    [5, 6, 7, 8],
  ],
  // trunk = 4
  [
    [3, 5, 6, 7],
    [5, 6, 7, 8],
    [6, 7, 8, 9],
  ],
  // trunk = 5
  [
    [4, 6, 7, 8],
    [6, 7, 8, 9],
    [7, 8, 9, 9],
  ],
];

const REBA_UPPER_ARM: Record<RebaUpperArm, number> = {
  extend_20_to_flex_20: 1,
  extend_gt_20_or_flex_20_45: 2,
  flex_45_90: 3,
  flex_gt_90: 4,
};

const REBA_LOWER_ARM: Record<RebaLowerArm, number> = {
  flex_60_100: 1,
  flex_lt_60_or_gt_100: 2,
};

const REBA_WRIST: Record<RebaWrist, number> = {
  flex_or_extend_0_15: 1,
  flex_or_extend_gt_15: 2,
};

// REBA Table B — Upper arm (1..6) × Lower arm (1..2) × Wrist (1..3) → 1..9
// Indexed [upper-1][lower-1][wrist-1].
const REBA_TABLE_B: ReadonlyArray<ReadonlyArray<ReadonlyArray<number>>> = [
  // upper = 1
  [
    [1, 2, 2],
    [1, 2, 3],
  ],
  // upper = 2
  [
    [1, 2, 3],
    [2, 3, 4],
  ],
  // upper = 3
  [
    [3, 4, 5],
    [4, 5, 5],
  ],
  // upper = 4
  [
    [4, 5, 5],
    [5, 6, 7],
  ],
  // upper = 5
  [
    [6, 7, 8],
    [7, 8, 8],
  ],
  // upper = 6
  [
    [7, 8, 8],
    [8, 9, 9],
  ],
];

const REBA_COUPLING: Record<RebaCoupling, number> = {
  good: 0,
  fair: 1,
  poor: 2,
  unacceptable: 3,
};

// REBA Table C — Score A (1..12) × Score B (1..12) → 1..12
// Source: Hignett & McAtamney (2000) Table C.
const REBA_TABLE_C: ReadonlyArray<ReadonlyArray<number>> = [
  [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
  [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
  [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8],
  [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9],
  [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
  [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10],
  [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11],
  [8, 8, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11],
  [9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12],
  [10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12],
  [11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12],
  [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
];

function clampIndex(value: number, max: number): number {
  return Math.max(0, Math.min(max - 1, value - 1));
}

function rebaTrunkScore(inputs: RebaInputs): number {
  let s = REBA_TRUNK[inputs.trunk];
  if (inputs.trunk_twist_or_sidebend) s += 1;
  return s;
}

function rebaNeckScore(inputs: RebaInputs): number {
  let s = REBA_NECK[inputs.neck];
  if (inputs.neck_twist_or_sidebend) s += 1;
  return s;
}

function rebaLegScore(inputs: RebaInputs): number {
  let s = REBA_LEGS[inputs.legs];
  if (inputs.knee_flexion_30_60) s += 1;
  if (inputs.knee_flexion_gt_60_not_sitting) s += 2;
  return s;
}

function rebaUpperArmScore(inputs: RebaInputs): number {
  let s = REBA_UPPER_ARM[inputs.upper_arm];
  if (inputs.shoulder_raised) s += 1;
  if (inputs.arm_abducted) s += 1;
  if (inputs.arm_supported_or_leaning) s -= 1;
  return Math.max(1, s);
}

function rebaWristScore(inputs: RebaInputs): number {
  let s = REBA_WRIST[inputs.wrist];
  if (inputs.wrist_twisted_or_deviated) s += 1;
  return s;
}

/** REBA total score, with table-driven sub-scores and risk band. */
export function rebaScore(inputs: RebaInputs): RebaResult {
  const trunkScore = rebaTrunkScore(inputs);
  const neckScore = rebaNeckScore(inputs);
  const legScore = rebaLegScore(inputs);
  const upperArmScore = rebaUpperArmScore(inputs);
  const lowerArmScore = REBA_LOWER_ARM[inputs.lower_arm];
  const wristScore = rebaWristScore(inputs);

  const tableA =
    REBA_TABLE_A[clampIndex(trunkScore, REBA_TABLE_A.length)][
      clampIndex(neckScore, REBA_TABLE_A[0].length)
    ][clampIndex(legScore, REBA_TABLE_A[0][0].length)];

  let scoreA = tableA + inputs.load_score;
  if (inputs.shock_force) scoreA += 1;

  const tableB =
    REBA_TABLE_B[clampIndex(upperArmScore, REBA_TABLE_B.length)][
      clampIndex(lowerArmScore, REBA_TABLE_B[0].length)
    ][clampIndex(wristScore, REBA_TABLE_B[0][0].length)];

  const scoreB = tableB + REBA_COUPLING[inputs.coupling];

  const tableC =
    REBA_TABLE_C[clampIndex(scoreA, REBA_TABLE_C.length)][clampIndex(scoreB, REBA_TABLE_C[0].length)];

  let activity = 0;
  if (inputs.static_posture_gt_1min) activity += 1;
  if (inputs.repeated_actions_gt_4_per_min) activity += 1;
  if (inputs.rapid_or_unstable_actions) activity += 1;

  const final = tableC + activity;

  let risk: RebaResult['risk_level'];
  let action: string;
  if (final === 1) {
    risk = 'negligible';
    action = 'Negligible risk; no change necessary.';
  } else if (final <= 3) {
    risk = 'low';
    action = 'Low risk; change may be needed.';
  } else if (final <= 7) {
    risk = 'medium';
    action = 'Medium risk; further investigation, change soon.';
  } else if (final <= 10) {
    risk = 'high';
    action = 'High risk; investigate and implement change.';
  } else {
    risk = 'very_high';
    action = 'Very high risk; implement change now.';
  }

  return {
    reba_score: final,
    score_a: scoreA,
    score_b: scoreB,
    table_c: tableC,
    activity_score: activity,
    risk_level: risk,
    recommended_action: action,
  };
}

// ─── RULA ──────────────────────────────────────────────────────────────

export type RulaUpperArm =
  | 'extend_20_to_flex_20'
  | 'extend_gt_20_or_flex_20_45'
  | 'flex_45_90'
  | 'flex_gt_90';

export type RulaLowerArm = 'flex_60_100' | 'flex_0_60_or_gt_100';

export type RulaWrist = 'neutral' | 'flex_or_extend_0_15' | 'flex_or_extend_gt_15';

export type RulaWristTwist = 'mid_range' | 'near_end_of_range';

export type RulaNeck = 'flex_0_10' | 'flex_10_20' | 'flex_gt_20' | 'extension';

export type RulaTrunk =
  | 'sitting_supported'
  | 'flex_0_20'
  | 'flex_20_60'
  | 'flex_gt_60';

export type RulaLegs = 'balanced_supported' | 'unbalanced';

export type RulaForceLoad = 'lt_2kg_intermittent' | 'between_2_10kg_intermittent' | 'between_2_10kg_static_or_repeated' | 'gt_10kg_or_shock';

export interface RulaInputs {
  upper_arm: RulaUpperArm;
  shoulder_raised?: boolean;
  arm_abducted?: boolean;
  arm_supported_or_leaning?: boolean;
  lower_arm: RulaLowerArm;
  arm_across_midline_or_out_to_side?: boolean;
  wrist: RulaWrist;
  wrist_bent?: boolean;
  wrist_twist: RulaWristTwist;
  /** Group A muscle use: posture mainly static (>1 min) OR repeated >4/min. */
  group_a_static_or_repeated?: boolean;
  group_a_force_load: RulaForceLoad;

  neck: RulaNeck;
  neck_twist?: boolean;
  neck_sidebend?: boolean;
  trunk: RulaTrunk;
  trunk_twist?: boolean;
  trunk_sidebend?: boolean;
  legs: RulaLegs;
  group_b_static_or_repeated?: boolean;
  group_b_force_load: RulaForceLoad;
}

export interface RulaResult {
  rula_score: number;
  score_a: number;
  score_b: number;
  posture_a: number;
  posture_b: number;
  risk_level: 'acceptable' | 'investigate' | 'investigate_change_soon' | 'investigate_change_now';
  recommended_action: string;
}

const RULA_UPPER_ARM: Record<RulaUpperArm, number> = {
  extend_20_to_flex_20: 1,
  extend_gt_20_or_flex_20_45: 2,
  flex_45_90: 3,
  flex_gt_90: 4,
};

const RULA_LOWER_ARM: Record<RulaLowerArm, number> = {
  flex_60_100: 1,
  flex_0_60_or_gt_100: 2,
};

const RULA_WRIST: Record<RulaWrist, number> = {
  neutral: 1,
  flex_or_extend_0_15: 2,
  flex_or_extend_gt_15: 3,
};

const RULA_WRIST_TWIST: Record<RulaWristTwist, number> = {
  mid_range: 1,
  near_end_of_range: 2,
};

const RULA_NECK: Record<RulaNeck, number> = {
  flex_0_10: 1,
  flex_10_20: 2,
  flex_gt_20: 3,
  extension: 4,
};

const RULA_TRUNK: Record<RulaTrunk, number> = {
  sitting_supported: 1,
  flex_0_20: 2,
  flex_20_60: 3,
  flex_gt_60: 4,
};

const RULA_LEGS: Record<RulaLegs, number> = {
  balanced_supported: 1,
  unbalanced: 2,
};

const RULA_FORCE: Record<RulaForceLoad, number> = {
  lt_2kg_intermittent: 0,
  between_2_10kg_intermittent: 1,
  between_2_10kg_static_or_repeated: 2,
  gt_10kg_or_shock: 3,
};

// RULA Table A — UpperArm × LowerArm × Wrist × WristTwist → 1..9
// Indexed [upper-1][lower-1][wrist-1][twist-1].
// Values from McAtamney & Corlett (1993), Figure 5.
const RULA_TABLE_A: ReadonlyArray<ReadonlyArray<ReadonlyArray<ReadonlyArray<number>>>> = [
  // upper = 1
  [
    [
      [1, 2],
      [2, 2],
      [2, 3],
    ],
    [
      [2, 2],
      [2, 2],
      [2, 3],
    ],
    [
      [2, 3],
      [3, 3],
      [3, 3],
    ],
  ],
  // upper = 2
  [
    [
      [2, 3],
      [3, 3],
      [3, 4],
    ],
    [
      [3, 3],
      [3, 3],
      [3, 4],
    ],
    [
      [3, 4],
      [4, 4],
      [4, 4],
    ],
  ],
  // upper = 3
  [
    [
      [3, 3],
      [4, 4],
      [4, 4],
    ],
    [
      [3, 4],
      [4, 4],
      [4, 4],
    ],
    [
      [4, 4],
      [4, 4],
      [4, 5],
    ],
  ],
  // upper = 4
  [
    [
      [4, 4],
      [4, 4],
      [4, 5],
    ],
    [
      [4, 4],
      [4, 4],
      [4, 5],
    ],
    [
      [4, 4],
      [4, 5],
      [5, 5],
    ],
  ],
  // upper = 5
  [
    [
      [5, 5],
      [5, 5],
      [5, 6],
    ],
    [
      [5, 6],
      [6, 6],
      [6, 7],
    ],
    [
      [6, 6],
      [6, 7],
      [7, 7],
    ],
  ],
  // upper = 6
  [
    [
      [7, 7],
      [7, 7],
      [7, 8],
    ],
    [
      [8, 8],
      [8, 8],
      [8, 9],
    ],
    [
      [9, 9],
      [9, 9],
      [9, 9],
    ],
  ],
];

// RULA Table B — Neck × Trunk × Legs → 1..9
// Indexed [neck-1][trunk-1][legs-1].
const RULA_TABLE_B: ReadonlyArray<ReadonlyArray<ReadonlyArray<number>>> = [
  // neck = 1
  [
    [1, 3],
    [2, 3],
    [3, 4],
    [5, 5],
    [6, 6],
    [7, 7],
  ],
  // neck = 2
  [
    [2, 3],
    [2, 3],
    [4, 5],
    [5, 5],
    [6, 7],
    [7, 7],
  ],
  // neck = 3
  [
    [3, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [6, 7],
    [7, 7],
  ],
  // neck = 4
  [
    [5, 5],
    [5, 6],
    [6, 7],
    [7, 7],
    [7, 7],
    [8, 8],
  ],
  // neck = 5
  [
    [7, 7],
    [7, 7],
    [7, 8],
    [8, 8],
    [8, 8],
    [8, 8],
  ],
  // neck = 6
  [
    [8, 8],
    [8, 8],
    [8, 8],
    [8, 9],
    [9, 9],
    [9, 9],
  ],
];

// RULA Grand Score Table C — Score A (1..8) × Score B (1..7) → 1..7
const RULA_TABLE_C: ReadonlyArray<ReadonlyArray<number>> = [
  [1, 2, 3, 3, 4, 5, 5],
  [2, 2, 3, 4, 4, 5, 5],
  [3, 3, 3, 4, 4, 5, 6],
  [3, 3, 3, 4, 5, 6, 6],
  [4, 4, 4, 5, 6, 7, 7],
  [4, 4, 5, 6, 6, 7, 7],
  [5, 5, 6, 6, 7, 7, 7],
  [5, 5, 6, 7, 7, 7, 7],
];

function rulaUpperArmScore(inputs: RulaInputs): number {
  let s = RULA_UPPER_ARM[inputs.upper_arm];
  if (inputs.shoulder_raised) s += 1;
  if (inputs.arm_abducted) s += 1;
  if (inputs.arm_supported_or_leaning) s -= 1;
  return Math.max(1, s);
}

function rulaLowerArmScore(inputs: RulaInputs): number {
  let s = RULA_LOWER_ARM[inputs.lower_arm];
  if (inputs.arm_across_midline_or_out_to_side) s += 1;
  return s;
}

function rulaWristScore(inputs: RulaInputs): number {
  let s = RULA_WRIST[inputs.wrist];
  if (inputs.wrist_bent) s += 1;
  return s;
}

function rulaNeckScore(inputs: RulaInputs): number {
  let s = RULA_NECK[inputs.neck];
  if (inputs.neck_twist) s += 1;
  if (inputs.neck_sidebend) s += 1;
  return s;
}

function rulaTrunkScore(inputs: RulaInputs): number {
  let s = RULA_TRUNK[inputs.trunk];
  if (inputs.trunk_twist) s += 1;
  if (inputs.trunk_sidebend) s += 1;
  return s;
}

/** RULA grand score (1–7) with table-driven sub-scores and risk band. */
export function rulaScore(inputs: RulaInputs): RulaResult {
  const upper = rulaUpperArmScore(inputs);
  const lower = rulaLowerArmScore(inputs);
  const wrist = rulaWristScore(inputs);
  const wristTwist = RULA_WRIST_TWIST[inputs.wrist_twist];

  const postureA =
    RULA_TABLE_A[clampIndex(upper, RULA_TABLE_A.length)][clampIndex(lower, RULA_TABLE_A[0].length)][
      clampIndex(wrist, RULA_TABLE_A[0][0].length)
    ][clampIndex(wristTwist, RULA_TABLE_A[0][0][0].length)];

  let scoreA = postureA + (inputs.group_a_static_or_repeated ? 1 : 0) + RULA_FORCE[inputs.group_a_force_load];

  const neck = rulaNeckScore(inputs);
  const trunk = rulaTrunkScore(inputs);
  const legs = RULA_LEGS[inputs.legs];

  const postureB =
    RULA_TABLE_B[clampIndex(neck, RULA_TABLE_B.length)][clampIndex(trunk, RULA_TABLE_B[0].length)][
      clampIndex(legs, RULA_TABLE_B[0][0].length)
    ];

  let scoreB = postureB + (inputs.group_b_static_or_repeated ? 1 : 0) + RULA_FORCE[inputs.group_b_force_load];

  // Cap inputs to the published Grand Score table dimensions.
  scoreA = Math.min(8, Math.max(1, scoreA));
  scoreB = Math.min(7, Math.max(1, scoreB));

  const grand = RULA_TABLE_C[scoreA - 1][scoreB - 1];

  let risk: RulaResult['risk_level'];
  let action: string;
  if (grand <= 2) {
    risk = 'acceptable';
    action = 'Acceptable posture; no action required.';
  } else if (grand <= 4) {
    risk = 'investigate';
    action = 'Further investigation; change may be needed.';
  } else if (grand <= 6) {
    risk = 'investigate_change_soon';
    action = 'Investigate further; change soon.';
  } else {
    risk = 'investigate_change_now';
    action = 'Investigate and implement change now.';
  }

  return {
    rula_score: grand,
    score_a: scoreA,
    score_b: scoreB,
    posture_a: postureA,
    posture_b: postureB,
    risk_level: risk,
    recommended_action: action,
  };
}
