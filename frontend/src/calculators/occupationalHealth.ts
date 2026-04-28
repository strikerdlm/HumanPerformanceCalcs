/**
 * Occupational Health Calculations for the Aerospace Industry.
 *
 * Implements:
 *   - Time-Weighted Average (TWA) exposure
 *   - Brief & Scala adjustment for unusual work schedules
 *   - Mixed-exposure additive index
 *   - Per-chemical risk assessment vs ACGIH TLV
 *   - Permissible exposure time (Haber's rule)
 *   - Biological Exposure Index (BEI) assessment
 *   - Plain-text exposure report generator
 *
 * Educational/research use only. Reference standards:
 *   - ACGIH TLVs & BEIs (2024)
 *   - NIOSH Criteria Documents
 *   - OSHA aerospace-industry standards
 *   - Aerospace Medical Association guidelines
 */

export type ChemicalUnits = 'ppm' | 'mg/m³';

export interface ChemicalExposureData {
  name: string;
  cas_number: string;
  /** TLV 8h TWA in `units`. */
  tlv_twa: number;
  /** 15-min STEL in `units`, if defined. */
  tlv_stel: number | null;
  /** Ceiling limit in `units`, if defined. */
  tlv_ceiling: number | null;
  units: ChemicalUnits;
  critical_effects: string;
  bei_value?: number | null;
  bei_units?: string | null;
  skin_notation?: boolean;
  carcinogen?: boolean;
}

export const AEROSPACE_CHEMICALS: Record<string, ChemicalExposureData> = {
  hydrazine: {
    name: 'Hydrazine',
    cas_number: '302-01-2',
    tlv_twa: 0.01,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Cancer; skin and respiratory sensitization',
    skin_notation: true,
    carcinogen: true,
  },
  udmh: {
    name: '1,1-Dimethylhydrazine (UDMH)',
    cas_number: '57-14-7',
    tlv_twa: 0.01,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Cancer; liver damage; CNS effects',
    skin_notation: true,
    carcinogen: true,
  },
  mmh: {
    name: 'Monomethylhydrazine (MMH)',
    cas_number: '60-34-4',
    tlv_twa: 0.01,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Cancer; liver damage; CNS effects',
    skin_notation: true,
    carcinogen: true,
  },
  jet_fuel_jp8: {
    name: 'Jet Fuel (JP-8)',
    cas_number: '8008-20-6',
    tlv_twa: 200,
    tlv_stel: 250,
    tlv_ceiling: null,
    units: 'mg/m³',
    critical_effects: 'CNS depression; respiratory irritation',
    skin_notation: true,
    carcinogen: false,
  },
  nitrogen_tetroxide: {
    name: 'Nitrogen Tetroxide (NTO)',
    cas_number: '10544-72-6',
    tlv_twa: 1,
    tlv_stel: 3,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Pulmonary edema; respiratory irritation',
    carcinogen: false,
  },
  benzene: {
    name: 'Benzene',
    cas_number: '71-43-2',
    tlv_twa: 0.02,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Leukemia; aplastic anemia',
    bei_value: 25,
    bei_units: 'μg/g creatinine',
    carcinogen: true,
  },
  toluene: {
    name: 'Toluene',
    cas_number: '108-88-3',
    tlv_twa: 20,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'CNS depression; developmental effects',
    bei_value: 0.03,
    bei_units: 'mg/L',
    skin_notation: true,
  },
  methylene_chloride: {
    name: 'Methylene Chloride',
    cas_number: '75-09-2',
    tlv_twa: 50,
    tlv_stel: null,
    tlv_ceiling: null,
    units: 'ppm',
    critical_effects: 'Cancer; CNS effects; liver damage',
    carcinogen: true,
  },
};

export type ExposureRiskLevel = 'Low' | 'Moderate' | 'High' | 'Very High';

export interface ExposureRiskAssessment {
  chemical: string;
  cas_number: string;
  measured_concentration: number;
  twa_exposure: number;
  tlv_twa: number;
  tlv_ratio: number;
  units: ChemicalUnits;
  risk_level: ExposureRiskLevel;
  recommendation: string;
  stel_exceeded: boolean;
  critical_effects: string;
  carcinogen: boolean;
  skin_notation: boolean;
}

export interface BeiAssessment {
  chemical: string;
  bei_available: boolean;
  measured_concentration?: number;
  bei_value?: number;
  bei_units?: string;
  bei_ratio?: number;
  assessment?: string;
  recommended_action?: string;
  sample_timing?: string;
  message?: string;
}

/**
 * Compute 8-hour Time-Weighted Average exposure: Σ(Cᵢ·tᵢ) / 8.
 *
 * @param concentrations Concentrations (ppm or mg/m³) per segment
 * @param durations_hours Hours per segment (must sum to ≤ 8)
 */
export function calculateTwaExposure(
  concentrations: number[],
  durations_hours: number[]
): number {
  if (concentrations.length !== durations_hours.length) {
    throw new Error('Concentrations and durations must have the same length');
  }
  const totalHours = durations_hours.reduce((a, b) => a + b, 0);
  if (totalHours > 8.0) {
    throw new Error('Total exposure time cannot exceed 8 hours');
  }
  let total = 0;
  for (let i = 0; i < concentrations.length; i++) {
    total += concentrations[i] * durations_hours[i];
  }
  return total / 8.0;
}

/**
 * Brief & Scala adjusted TLV for unusual work schedules.
 *
 * adj = (8 / hpd) × ((24 − 8) / (24 − hpd)) × (5 / dpw)
 */
export function calculateAdjustedTlvUnusualSchedule(
  tlv_twa: number,
  hours_per_day: number,
  days_per_week: number,
  _weeks_per_year: number = 50
): number {
  const exposureFactor = 8.0 / hours_per_day;
  const recoveryFactor = (24 - 8) / (24 - hours_per_day);
  const weeklyFactor = 5.0 / days_per_week;
  return tlv_twa * exposureFactor * recoveryFactor * weeklyFactor;
}

/**
 * Mixed-exposure additive index Σ(Cᵢ / TLVᵢ). ≤ 1.0 is acceptable.
 *
 * Skips chemical names that are not in `AEROSPACE_CHEMICALS`.
 */
export function calculateMixedExposureIndex(
  exposures: Record<string, number>,
  chemical_names: string[]
): number {
  let index = 0;
  for (const name of chemical_names) {
    const exposure = exposures[name];
    const chem = AEROSPACE_CHEMICALS[name];
    if (exposure !== undefined && chem) {
      index += exposure / chem.tlv_twa;
    }
  }
  return index;
}

/** Assess occupational exposure risk for a single chemical. */
export function assessExposureRisk(
  chemical_name: string,
  measured_concentration: number,
  exposure_duration_hours: number = 8.0
): ExposureRiskAssessment {
  const chem = AEROSPACE_CHEMICALS[chemical_name];
  if (!chem) {
    throw new Error(`Chemical '${chemical_name}' not found in database`);
  }

  const twa =
    exposure_duration_hours === 8.0
      ? measured_concentration
      : (measured_concentration * exposure_duration_hours) / 8.0;
  const tlvRatio = twa / chem.tlv_twa;

  let risk: ExposureRiskLevel;
  let recommendation: string;
  if (tlvRatio <= 0.5) {
    risk = 'Low';
    recommendation = 'Exposure well below TLV. Continue monitoring.';
  } else if (tlvRatio <= 1.0) {
    risk = 'Moderate';
    recommendation = 'Exposure approaching TLV. Implement controls to reduce exposure.';
  } else if (tlvRatio <= 2.0) {
    risk = 'High';
    recommendation = 'Exposure exceeds TLV. Immediate action required to reduce exposure.';
  } else {
    risk = 'Very High';
    recommendation =
      'Exposure significantly exceeds TLV. Stop work and implement emergency controls.';
  }

  let stelExceeded = false;
  if (chem.tlv_stel !== null && chem.tlv_stel !== undefined && measured_concentration > chem.tlv_stel) {
    stelExceeded = true;
    if (risk === 'Low') risk = 'High';
  }

  return {
    chemical: chem.name,
    cas_number: chem.cas_number,
    measured_concentration,
    twa_exposure: twa,
    tlv_twa: chem.tlv_twa,
    tlv_ratio: tlvRatio,
    units: chem.units,
    risk_level: risk,
    recommendation,
    stel_exceeded: stelExceeded,
    critical_effects: chem.critical_effects,
    carcinogen: chem.carcinogen ?? false,
    skin_notation: chem.skin_notation ?? false,
  };
}

/**
 * Maximum permissible exposure time (Haber's rule: C × t = TLV × 8).
 * Returns hours, capped at 8.
 */
export function calculatePermissibleExposureTime(
  chemical_name: string,
  measured_concentration: number
): number {
  const chem = AEROSPACE_CHEMICALS[chemical_name];
  if (!chem) {
    throw new Error(`Chemical '${chemical_name}' not found in database`);
  }
  if (measured_concentration <= 0) return 8.0;
  const max = (chem.tlv_twa * 8.0) / measured_concentration;
  return Math.min(max, 8.0);
}

/**
 * Plain-text exposure report (mirrors the Python `generate_exposure_report`).
 *
 * `exposures` keys must be members of `AEROSPACE_CHEMICALS`.
 */
export function generateExposureReport(
  facility_name: string,
  assessment_date: string,
  exposures: Record<string, { concentration: number; duration?: number }>
): string {
  let report = `\nAEROSPACE OCCUPATIONAL HEALTH EXPOSURE ASSESSMENT REPORT\n=======================================================\n\nFacility: ${facility_name}\nAssessment Date: ${assessment_date}\nStandard: ACGIH TLVs and BEIs (2024)\n\nINDIVIDUAL CHEMICAL ASSESSMENTS:\n-------------------------------\n`;

  let totalMixedIndex = 0;
  const highRisk: string[] = [];

  for (const [chemical, data] of Object.entries(exposures)) {
    if (!(chemical in AEROSPACE_CHEMICALS)) continue;
    const concentration = data.concentration ?? 0;
    const duration = data.duration ?? 8.0;
    const a = assessExposureRisk(chemical, concentration, duration);
    report +=
      `\nChemical: ${a.chemical} (CAS: ${a.cas_number})\n` +
      `Measured Concentration: ${a.measured_concentration.toFixed(3)} ${a.units}\n` +
      `8-hr TWA Exposure: ${a.twa_exposure.toFixed(3)} ${a.units}\n` +
      `TLV-TWA: ${a.tlv_twa.toFixed(3)} ${a.units}\n` +
      `TLV Ratio: ${a.tlv_ratio.toFixed(2)}\n` +
      `Risk Level: ${a.risk_level}\n` +
      `Recommendation: ${a.recommendation}\n` +
      `Critical Effects: ${a.critical_effects}\n`;
    if (a.carcinogen) {
      report += '⚠️  CARCINOGEN - Minimize exposure to lowest feasible level\n';
    }
    if (a.skin_notation) {
      report += '👤 SKIN NOTATION - Prevent skin contact\n';
    }
    if (a.stel_exceeded) {
      report += '🚨 STEL EXCEEDED - Short-term exposure limit violated\n';
    }
    if (a.risk_level === 'High' || a.risk_level === 'Very High') {
      highRisk.push(chemical);
    }
    totalMixedIndex += a.tlv_ratio;
  }

  report +=
    `\n\nMIXED EXPOSURE ASSESSMENT:\n-------------------------\n` +
    `Total Mixed Exposure Index: ${totalMixedIndex.toFixed(2)}\n`;
  if (totalMixedIndex <= 1.0) {
    report += '✅ Mixed exposure within acceptable limits\n';
  } else {
    report += '❌ Mixed exposure exceeds acceptable limits - Immediate action required\n';
  }
  if (highRisk.length > 0) {
    report += `\n🚨 HIGH RISK CHEMICALS IDENTIFIED: ${highRisk.join(', ')}\n`;
  }

  report +=
    '\n\nRECOMMENDATIONS:\n---------------\n' +
    '1. Implement engineering controls to reduce exposure levels\n' +
    '2. Provide appropriate respiratory protection where needed\n' +
    '3. Conduct regular air monitoring\n' +
    '4. Provide worker training on chemical hazards\n' +
    '5. Implement medical surveillance program\n' +
    '6. Maintain exposure records per regulatory requirements\n\n' +
    'For technical questions, consult with a Certified Industrial Hygienist (CIH).\n\n' +
    'This assessment is for educational purposes only and should not replace \n' +
    'professional industrial hygiene evaluation.\n';

  return report;
}

/** Assess a biomarker measurement against the ACGIH BEI for the chemical. */
export function calculateBiologicalExposureIndex(
  chemical_name: string,
  biomarker_concentration: number,
  sample_timing: string = 'end_of_shift'
): BeiAssessment {
  const chem = AEROSPACE_CHEMICALS[chemical_name];
  if (!chem) {
    throw new Error(`Chemical '${chemical_name}' not found in database`);
  }
  if (chem.bei_value === undefined || chem.bei_value === null) {
    return {
      chemical: chem.name,
      bei_available: false,
      message: 'No BEI established for this chemical',
    };
  }

  const ratio = biomarker_concentration / chem.bei_value;
  const assessment = ratio <= 1.0 ? 'Within BEI guideline' : 'Exceeds BEI guideline';
  const action =
    ratio <= 1.0
      ? 'Continue current practices'
      : 'Investigate exposure sources and implement controls';

  return {
    chemical: chem.name,
    bei_available: true,
    measured_concentration: biomarker_concentration,
    bei_value: chem.bei_value,
    bei_units: chem.bei_units ?? undefined,
    bei_ratio: ratio,
    assessment,
    recommended_action: action,
    sample_timing,
  };
}
