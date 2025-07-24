"""
Occupational Health Calculations for Aerospace Industry
Author: Diego Malpica

Usage:
    Provides functions to compute occupational exposure limits, time-weighted averages,
    and biological exposure indices for common aerospace chemicals based on ACGIH TLV/BEI standards.
    For educational and research use in aerospace occupational health and industrial hygiene.

Scientific Sources:
    - ACGIH TLVs and BEIs (2024)
    - NIOSH Criteria Documents
    - OSHA Standards for Aerospace Industry
    - Aerospace Medical Association Guidelines
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ChemicalExposureData:
    """Data structure for chemical exposure information."""
    name: str
    cas_number: str
    tlv_twa: float  # ppm or mg/m³
    tlv_stel: Optional[float]  # 15-min STEL
    tlv_ceiling: Optional[float]  # Ceiling limit
    units: str  # "ppm" or "mg/m³"
    critical_effects: str
    bei_value: Optional[float] = None
    bei_units: Optional[str] = None
    skin_notation: bool = False
    carcinogen: bool = False


# ACGIH TLV/BEI data for common aerospace industry chemicals
AEROSPACE_CHEMICALS = {
    "hydrazine": ChemicalExposureData(
        name="Hydrazine",
        cas_number="302-01-2",
        tlv_twa=0.01,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Cancer; skin and respiratory sensitization",
        skin_notation=True,
        carcinogen=True
    ),
    "udmh": ChemicalExposureData(
        name="1,1-Dimethylhydrazine (UDMH)",
        cas_number="57-14-7",
        tlv_twa=0.01,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Cancer; liver damage; CNS effects",
        skin_notation=True,
        carcinogen=True
    ),
    "mmh": ChemicalExposureData(
        name="Monomethylhydrazine (MMH)",
        cas_number="60-34-4",
        tlv_twa=0.01,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Cancer; liver damage; CNS effects",
        skin_notation=True,
        carcinogen=True
    ),
    "jet_fuel_jp8": ChemicalExposureData(
        name="Jet Fuel (JP-8)",
        cas_number="8008-20-6",
        tlv_twa=200,
        tlv_stel=250,
        tlv_ceiling=None,
        units="mg/m³",
        critical_effects="CNS depression; respiratory irritation",
        skin_notation=True,
        carcinogen=False
    ),
    "nitrogen_tetroxide": ChemicalExposureData(
        name="Nitrogen Tetroxide (NTO)",
        cas_number="10544-72-6",
        tlv_twa=1,
        tlv_stel=3,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Pulmonary edema; respiratory irritation",
        carcinogen=False
    ),
    "benzene": ChemicalExposureData(
        name="Benzene",
        cas_number="71-43-2",
        tlv_twa=0.02,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Leukemia; aplastic anemia",
        bei_value=25,
        bei_units="μg/g creatinine",
        carcinogen=True
    ),
    "toluene": ChemicalExposureData(
        name="Toluene",
        cas_number="108-88-3",
        tlv_twa=20,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="CNS depression; developmental effects",
        bei_value=0.03,
        bei_units="mg/L",
        skin_notation=True
    ),
    "methylene_chloride": ChemicalExposureData(
        name="Methylene Chloride",
        cas_number="75-09-2",
        tlv_twa=50,
        tlv_stel=None,
        tlv_ceiling=None,
        units="ppm",
        critical_effects="Cancer; CNS effects; liver damage",
        carcinogen=True
    )
}


def calculate_twa_exposure(concentrations: List[float], durations: List[float]) -> float:
    """
    Calculate 8-hour time-weighted average exposure.
    
    Args:
        concentrations: List of exposure concentrations (ppm or mg/m³)
        durations: List of exposure durations (hours)
    
    Returns:
        8-hour TWA exposure value
    """
    if len(concentrations) != len(durations):
        raise ValueError("Concentrations and durations must have the same length")
    
    if sum(durations) > 8.0:
        raise ValueError("Total exposure time cannot exceed 8 hours")
    
    total_exposure = sum(c * d for c, d in zip(concentrations, durations))
    return total_exposure / 8.0


def calculate_adjusted_tlv_unusual_schedule(
    tlv_twa: float,
    hours_per_day: float,
    days_per_week: float,
    weeks_per_year: float = 50
) -> float:
    """
    Calculate adjusted TLV for unusual work schedules using Brief & Scala model.
    
    Args:
        tlv_twa: Standard 8-hour TWA TLV
        hours_per_day: Actual hours worked per day
        days_per_week: Actual days worked per week
        weeks_per_year: Weeks worked per year
    
    Returns:
        Adjusted TLV for the unusual work schedule
    """
    # Brief & Scala adjustment factors
    exposure_factor = 8.0 / hours_per_day
    recovery_factor = (24 - 8) / (24 - hours_per_day)
    weekly_factor = 5.0 / days_per_week
    
    adjustment_factor = exposure_factor * recovery_factor * weekly_factor
    
    return tlv_twa * adjustment_factor


def calculate_mixed_exposure_index(exposures: Dict[str, float], chemical_names: List[str]) -> float:
    """
    Calculate mixed exposure index for multiple chemicals with similar effects.
    
    Args:
        exposures: Dictionary of chemical exposures {chemical_name: exposure_level}
        chemical_names: List of chemical names to include in calculation
    
    Returns:
        Mixed exposure index (should be ≤ 1.0 for acceptable exposure)
    """
    index = 0.0
    
    for chem_name in chemical_names:
        if chem_name in exposures and chem_name in AEROSPACE_CHEMICALS:
            exposure = exposures[chem_name]
            tlv = AEROSPACE_CHEMICALS[chem_name].tlv_twa
            index += exposure / tlv
    
    return index


def assess_exposure_risk(
    chemical_name: str,
    measured_concentration: float,
    exposure_duration: float = 8.0
) -> Dict[str, any]:
    """
    Assess occupational exposure risk for a specific chemical.
    
    Args:
        chemical_name: Name of the chemical (key in AEROSPACE_CHEMICALS)
        measured_concentration: Measured concentration (ppm or mg/m³)
        exposure_duration: Exposure duration in hours
    
    Returns:
        Dictionary containing risk assessment results
    """
    if chemical_name not in AEROSPACE_CHEMICALS:
        raise ValueError(f"Chemical '{chemical_name}' not found in database")
    
    chem_data = AEROSPACE_CHEMICALS[chemical_name]
    
    # Calculate TWA if exposure is not 8 hours
    if exposure_duration != 8.0:
        twa_exposure = (measured_concentration * exposure_duration) / 8.0
    else:
        twa_exposure = measured_concentration
    
    # Compare to TLV-TWA
    tlv_ratio = twa_exposure / chem_data.tlv_twa
    
    # Determine risk level
    if tlv_ratio <= 0.5:
        risk_level = "Low"
        recommendation = "Exposure well below TLV. Continue monitoring."
    elif tlv_ratio <= 1.0:
        risk_level = "Moderate"
        recommendation = "Exposure approaching TLV. Implement controls to reduce exposure."
    elif tlv_ratio <= 2.0:
        risk_level = "High"
        recommendation = "Exposure exceeds TLV. Immediate action required to reduce exposure."
    else:
        risk_level = "Very High"
        recommendation = "Exposure significantly exceeds TLV. Stop work and implement emergency controls."
    
    # Check STEL if applicable
    stel_exceeded = False
    if chem_data.tlv_stel and measured_concentration > chem_data.tlv_stel:
        stel_exceeded = True
        risk_level = "High" if risk_level == "Low" else risk_level
    
    return {
        "chemical": chem_data.name,
        "cas_number": chem_data.cas_number,
        "measured_concentration": measured_concentration,
        "twa_exposure": twa_exposure,
        "tlv_twa": chem_data.tlv_twa,
        "tlv_ratio": tlv_ratio,
        "units": chem_data.units,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "stel_exceeded": stel_exceeded,
        "critical_effects": chem_data.critical_effects,
        "carcinogen": chem_data.carcinogen,
        "skin_notation": chem_data.skin_notation
    }


def calculate_permissible_exposure_time(
    chemical_name: str,
    measured_concentration: float
) -> float:
    """
    Calculate maximum permissible exposure time based on concentration.
    
    Args:
        chemical_name: Name of the chemical
        measured_concentration: Measured concentration
    
    Returns:
        Maximum permissible exposure time in hours
    """
    if chemical_name not in AEROSPACE_CHEMICALS:
        raise ValueError(f"Chemical '{chemical_name}' not found in database")
    
    chem_data = AEROSPACE_CHEMICALS[chemical_name]
    
    if measured_concentration <= 0:
        return 8.0
    
    # Using Haber's rule: C × t = constant
    max_time = (chem_data.tlv_twa * 8.0) / measured_concentration
    
    return min(max_time, 8.0)  # Cap at 8 hours


def generate_exposure_report(
    facility_name: str,
    assessment_date: str,
    exposures: Dict[str, Dict[str, float]]
) -> str:
    """
    Generate a comprehensive exposure assessment report.
    
    Args:
        facility_name: Name of the facility
        assessment_date: Date of assessment
        exposures: Dictionary of exposures {chemical: {concentration: float, duration: float}}
    
    Returns:
        Formatted exposure assessment report
    """
    report = f"""
AEROSPACE OCCUPATIONAL HEALTH EXPOSURE ASSESSMENT REPORT
=======================================================

Facility: {facility_name}
Assessment Date: {assessment_date}
Standard: ACGIH TLVs and BEIs (2024)

INDIVIDUAL CHEMICAL ASSESSMENTS:
-------------------------------
"""
    
    total_mixed_index = 0.0
    high_risk_chemicals = []
    
    for chemical, data in exposures.items():
        if chemical in AEROSPACE_CHEMICALS:
            concentration = data.get('concentration', 0)
            duration = data.get('duration', 8.0)
            
            assessment = assess_exposure_risk(chemical, concentration, duration)
            
            report += f"""
Chemical: {assessment['chemical']} (CAS: {assessment['cas_number']})
Measured Concentration: {assessment['measured_concentration']:.3f} {assessment['units']}
8-hr TWA Exposure: {assessment['twa_exposure']:.3f} {assessment['units']}
TLV-TWA: {assessment['tlv_twa']:.3f} {assessment['units']}
TLV Ratio: {assessment['tlv_ratio']:.2f}
Risk Level: {assessment['risk_level']}
Recommendation: {assessment['recommendation']}
Critical Effects: {assessment['critical_effects']}
"""
            
            if assessment['carcinogen']:
                report += "⚠️  CARCINOGEN - Minimize exposure to lowest feasible level\n"
            
            if assessment['skin_notation']:
                report += "👤 SKIN NOTATION - Prevent skin contact\n"
            
            if assessment['stel_exceeded']:
                report += "🚨 STEL EXCEEDED - Short-term exposure limit violated\n"
            
            if assessment['risk_level'] in ['High', 'Very High']:
                high_risk_chemicals.append(chemical)
            
            total_mixed_index += assessment['tlv_ratio']
    
    report += f"""

MIXED EXPOSURE ASSESSMENT:
-------------------------
Total Mixed Exposure Index: {total_mixed_index:.2f}
"""
    
    if total_mixed_index <= 1.0:
        report += "✅ Mixed exposure within acceptable limits\n"
    else:
        report += "❌ Mixed exposure exceeds acceptable limits - Immediate action required\n"
    
    if high_risk_chemicals:
        report += f"\n🚨 HIGH RISK CHEMICALS IDENTIFIED: {', '.join(high_risk_chemicals)}\n"
    
    report += """

RECOMMENDATIONS:
---------------
1. Implement engineering controls to reduce exposure levels
2. Provide appropriate respiratory protection where needed
3. Conduct regular air monitoring
4. Provide worker training on chemical hazards
5. Implement medical surveillance program
6. Maintain exposure records per regulatory requirements

For technical questions, consult with a Certified Industrial Hygienist (CIH).

This assessment is for educational purposes only and should not replace 
professional industrial hygiene evaluation.
"""
    
    return report


def calculate_biological_exposure_index(
    chemical_name: str,
    biomarker_concentration: float,
    sample_timing: str = "end_of_shift"
) -> Dict[str, any]:
    """
    Calculate and assess biological exposure index (BEI) values.
    
    Args:
        chemical_name: Name of the chemical
        biomarker_concentration: Measured biomarker concentration
        sample_timing: Timing of sample collection
    
    Returns:
        BEI assessment results
    """
    if chemical_name not in AEROSPACE_CHEMICALS:
        raise ValueError(f"Chemical '{chemical_name}' not found in database")
    
    chem_data = AEROSPACE_CHEMICALS[chemical_name]
    
    if chem_data.bei_value is None:
        return {
            "chemical": chem_data.name,
            "bei_available": False,
            "message": "No BEI established for this chemical"
        }
    
    bei_ratio = biomarker_concentration / chem_data.bei_value
    
    if bei_ratio <= 1.0:
        assessment = "Within BEI guideline"
        action = "Continue current practices"
    else:
        assessment = "Exceeds BEI guideline"
        action = "Investigate exposure sources and implement controls"
    
    return {
        "chemical": chem_data.name,
        "bei_available": True,
        "measured_concentration": biomarker_concentration,
        "bei_value": chem_data.bei_value,
        "bei_units": chem_data.bei_units,
        "bei_ratio": bei_ratio,
        "assessment": assessment,
        "recommended_action": action,
        "sample_timing": sample_timing
    }