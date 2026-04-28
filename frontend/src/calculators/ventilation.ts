/**
 * Industrial ventilation and respiratory-protection helpers.
 *
 * Includes:
 *   - Dilution-ventilation airflow Q = G·K / TLV (ACGIH Industrial Ventilation
 *     Manual; assumes complete mixing)
 *   - Respirator Maximum Use Concentration (MUC) = APF · TLV with the OSHA
 *     APF table from 29 CFR 1910.134(d)(3)(i)
 *   - ASHRAE 62.1-2022 outdoor airflow Vbz = Rp·Pz + Ra·Az for typical
 *     occupancy categories (Table 6-1)
 *
 * Educational/research use only — not a substitute for site-specific
 * engineering design or compliance review.
 */

export type RespiratorClass =
  | 'half_mask_air_purifying'
  | 'full_face_air_purifying'
  | 'powered_air_purifying_loose_fitting'
  | 'powered_air_purifying_half_mask'
  | 'powered_air_purifying_full_face_helmet'
  | 'powered_air_purifying_tight_fitting_full_face'
  | 'supplied_air_demand_half_mask'
  | 'supplied_air_demand_full_face'
  | 'supplied_air_continuous_flow_loose_fitting'
  | 'supplied_air_continuous_flow_full_face'
  | 'supplied_air_pressure_demand_half_mask'
  | 'supplied_air_pressure_demand_full_face'
  | 'supplied_air_pressure_demand_with_aux_scba'
  | 'scba_demand_full_face'
  | 'scba_pressure_demand_full_face';

/** OSHA APF table — 29 CFR 1910.134(d)(3)(i)(A). */
export const OSHA_ASSIGNED_PROTECTION_FACTORS: Record<RespiratorClass, number> = {
  half_mask_air_purifying: 10,
  full_face_air_purifying: 50,
  powered_air_purifying_loose_fitting: 25,
  powered_air_purifying_half_mask: 50,
  powered_air_purifying_full_face_helmet: 25,
  powered_air_purifying_tight_fitting_full_face: 1000,
  supplied_air_demand_half_mask: 10,
  supplied_air_demand_full_face: 50,
  supplied_air_continuous_flow_loose_fitting: 25,
  supplied_air_continuous_flow_full_face: 1000,
  supplied_air_pressure_demand_half_mask: 50,
  supplied_air_pressure_demand_full_face: 1000,
  supplied_air_pressure_demand_with_aux_scba: 10000,
  scba_demand_full_face: 50,
  scba_pressure_demand_full_face: 10000,
};

function ensurePositiveFinite(name: string, v: number): number {
  if (!Number.isFinite(v) || v <= 0) {
    throw new Error(`${name} must be a finite, positive number`);
  }
  return v;
}

/**
 * Dilution-ventilation airflow for a steady contaminant generation rate.
 *
 *   Q [m³/min] = G · K / TLV
 *
 * G = generation rate of contaminant (mass or volume / time, units must
 * match TLV); K = mixing factor (ACGIH IVM uses 1–10 with 3 typical).
 *
 * Returns Q in the same volume units as G/TLV per minute (i.e., the user
 * supplies consistent units; the function does not convert).
 */
export function dilutionAirflow(args: {
  /** Generation rate G of the contaminant (e.g. L/min or mg/min). */
  generation_rate: number;
  /** Threshold limit value (same units as G). */
  tlv: number;
  /** Mixing factor K (1–10). 3 is a common default. */
  mixing_factor: number;
}): number {
  ensurePositiveFinite('generation_rate', args.generation_rate);
  ensurePositiveFinite('tlv', args.tlv);
  if (!Number.isFinite(args.mixing_factor) || args.mixing_factor < 1 || args.mixing_factor > 10) {
    throw new Error('mixing_factor must be in [1, 10]');
  }
  return (args.generation_rate * args.mixing_factor) / args.tlv;
}

/**
 * Respirator Maximum Use Concentration (MUC) per OSHA 1910.134.
 *
 *   MUC = APF · TLV
 *
 * MUC is then capped by IDLH (or equivalent) limits for the substance — that
 * cap is NOT applied here (caller must check IDLH separately).
 */
export function respiratorMaximumUseConcentration(args: {
  respirator: RespiratorClass;
  tlv: number;
}): { apf: number; muc: number; respirator: RespiratorClass } {
  const apf = OSHA_ASSIGNED_PROTECTION_FACTORS[args.respirator];
  if (apf === undefined) {
    throw new Error(`Unknown respirator class: ${args.respirator}`);
  }
  ensurePositiveFinite('tlv', args.tlv);
  return { apf, muc: apf * args.tlv, respirator: args.respirator };
}

export type Ashrae62Occupancy =
  | 'office_general'
  | 'classroom_5_to_8'
  | 'classroom_9_plus'
  | 'conference_meeting'
  | 'lobby_corridor'
  | 'auditorium_seating'
  | 'restaurant_dining'
  | 'health_care_exam_room'
  | 'retail_sales'
  | 'hotel_bedroom_living'
  | 'industrial_break_room'
  | 'lecture_classroom'
  | 'laboratory_general';

interface Ashrae62Rates {
  /** Outdoor air rate per person, L/(s·person). */
  rp_l_s_person: number;
  /** Outdoor air rate per area, L/(s·m²). */
  ra_l_s_m2: number;
  default_density_per_100m2: number;
}

/**
 * Selected ASHRAE 62.1-2022 Table 6-1 default outdoor-air rates.
 *
 * Not exhaustive — covers the office, education, assembly, retail, and
 * common-aerospace-lab categories Diego is most likely to use. For other
 * occupancy types refer to Table 6-1 directly.
 */
export const ASHRAE_62_1_RATES: Record<Ashrae62Occupancy, Ashrae62Rates> = {
  office_general: { rp_l_s_person: 2.5, ra_l_s_m2: 0.3, default_density_per_100m2: 5 },
  classroom_5_to_8: { rp_l_s_person: 5.0, ra_l_s_m2: 0.6, default_density_per_100m2: 25 },
  classroom_9_plus: { rp_l_s_person: 5.0, ra_l_s_m2: 0.6, default_density_per_100m2: 35 },
  conference_meeting: { rp_l_s_person: 2.5, ra_l_s_m2: 0.3, default_density_per_100m2: 50 },
  lobby_corridor: { rp_l_s_person: 0, ra_l_s_m2: 0.3, default_density_per_100m2: 0 },
  auditorium_seating: { rp_l_s_person: 2.5, ra_l_s_m2: 0.3, default_density_per_100m2: 150 },
  restaurant_dining: { rp_l_s_person: 3.8, ra_l_s_m2: 0.9, default_density_per_100m2: 70 },
  health_care_exam_room: { rp_l_s_person: 7.5, ra_l_s_m2: 0.9, default_density_per_100m2: 20 },
  retail_sales: { rp_l_s_person: 3.8, ra_l_s_m2: 0.6, default_density_per_100m2: 15 },
  hotel_bedroom_living: { rp_l_s_person: 2.5, ra_l_s_m2: 0.3, default_density_per_100m2: 10 },
  industrial_break_room: { rp_l_s_person: 2.5, ra_l_s_m2: 0.6, default_density_per_100m2: 25 },
  lecture_classroom: { rp_l_s_person: 3.8, ra_l_s_m2: 0.3, default_density_per_100m2: 65 },
  laboratory_general: { rp_l_s_person: 5.0, ra_l_s_m2: 0.9, default_density_per_100m2: 25 },
};

/**
 * ASHRAE 62.1-2022 breathing-zone outdoor airflow (L/s).
 *
 *   V_bz = R_p · P_z + R_a · A_z
 *
 * With:
 *   R_p in L/(s·person), P_z in occupants
 *   R_a in L/(s·m²),    A_z in m²
 *
 * Use the published occupancy `category`; if the actual peak occupancy is
 * unknown, supply `area_m2` and we fall back to Table 6-1 default density.
 */
export function ashrae62OutdoorAirflow(args: {
  category: Ashrae62Occupancy;
  area_m2: number;
  occupants?: number;
}): { vbz_l_s: number; rp_used: number; ra_used: number; effective_occupancy: number } {
  const rates = ASHRAE_62_1_RATES[args.category];
  if (!rates) throw new Error(`Unknown ASHRAE category: ${args.category}`);
  ensurePositiveFinite('area_m2', args.area_m2);

  const occupants =
    args.occupants !== undefined
      ? args.occupants
      : Math.ceil((rates.default_density_per_100m2 / 100) * args.area_m2);
  if (!Number.isFinite(occupants) || occupants < 0) {
    throw new Error('occupants must be a finite, non-negative number');
  }

  const vbz = rates.rp_l_s_person * occupants + rates.ra_l_s_m2 * args.area_m2;
  return {
    vbz_l_s: vbz,
    rp_used: rates.rp_l_s_person,
    ra_used: rates.ra_l_s_m2,
    effective_occupancy: occupants,
  };
}

/** Convert L/s → CFM (cubic feet per minute). */
export function lpsToCfm(l_s: number): number {
  return l_s * 2.11888;
}

/** Convert CFM → L/s. */
export function cfmToLps(cfm: number): number {
  return cfm / 2.11888;
}
