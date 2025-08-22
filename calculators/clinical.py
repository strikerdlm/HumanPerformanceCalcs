# -*- coding: utf-8 -*-
"""
Clinical calculation utilities used by the Streamlit app.

Includes:
- Basal Metabolic Rate (Mifflin–St Jeor)
- Body Surface Area (Boyd, DuBois & DuBois, Haycock, Mosteller)
- eGFR (CKD‑EPI 2009, creatinine only)
- PaO₂/FiO₂ ratio (P/F ratio)
- Oxygen Index (OI)
- 6‑Minute Walk Distance (Enright & Sherrill)

All inputs should use SI/clinical units noted in each function docstring.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, log10
from typing import Dict, Tuple


def bmr_mifflin_st_jeor(weight_kg: float, height_cm: float, age_yr: float, sex: str) -> float:
	"""Compute Basal Metabolic Rate using the Mifflin–St Jeor equation.

	Args:
		weight_kg: Weight in kilograms
		height_cm: Height in centimeters
		age_yr: Age in years
		sex: "male" or "female"
	Returns:
		Estimated BMR in kcal/day
	"""
	sex_l = sex.strip().lower()
	if sex_l in {"m", "male", "man"}:
		return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age_yr + 5.0
	elif sex_l in {"f", "female", "woman"}:
		return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age_yr - 161.0
	else:
		raise ValueError("sex must be 'male' or 'female'")


def bsa_boyd(weight_kg: float) -> float:
	"""Body Surface Area using Boyd (weight-only variant).

	This classic pediatric-focused variant does not use height; the screenshot reference
	uses grams and returns cm². We convert to m² for consistency.

	Formula (Boyd 1935, weight-only):
		BSA_cm2 = 4.688 × w_g^0.8168 − 0.0154 × log10(w_g)

	Args:
		weight_kg: Weight in kilograms
	Returns:
		BSA in square meters
	"""
	w_g = weight_kg * 1000.0
	bsa_cm2 = 4.688 * (w_g ** 0.8168) - 0.0154 * log10(max(w_g, 1.0))
	return bsa_cm2 / 10000.0  # cm² → m²


def bsa_dubois(height_cm: float, weight_kg: float) -> float:
	"""Body Surface Area by DuBois & DuBois (1916).

	BSA (m²) = 0.007184 × height_cm^0.725 × weight_kg^0.425
	"""
	return 0.007184 * (height_cm ** 0.725) * (weight_kg ** 0.425)


def bsa_haycock(height_cm: float, weight_kg: float) -> float:
	"""Body Surface Area by Haycock et al. (1978).

	BSA (m²) = 0.024265 × height_cm^0.3964 × weight_kg^0.5378
	"""
	return 0.024265 * (height_cm ** 0.3964) * (weight_kg ** 0.5378)


def bsa_mosteller(height_cm: float, weight_kg: float) -> float:
	"""Body Surface Area by Mosteller (1987).

	BSA (m²) = sqrt((height_cm × weight_kg) / 3600)
	"""
	return sqrt((height_cm * weight_kg) / 3600.0)


@dataclass
class EGFRResult:
	value_ml_min_1_73m2: float
	sex_correction: float
	race_correction: float


def egfr_ckd_epi_2009(scr_mg_dl: float, age_yr: float, sex: str, is_black: bool = False) -> EGFRResult:
	"""Calculate eGFR using the CKD‑EPI 2009 creatinine equation.

	GFR = 141 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^−1.209 × 0.993^age × 1.018(if female) × 1.159(if black)

	Args:
		scr_mg_dl: Serum creatinine in mg/dL
		age_yr: Age in years
		sex: "male" or "female"
		is_black: Race correction flag, per original 2009 paper
	Returns:
		EGFRResult with value in mL/min/1.73m²
	"""
	sex_l = sex.strip().lower()
	if sex_l in {"f", "female", "woman"}:
		k = 0.7
		alpha = -0.329
		sex_corr = 1.018
	elif sex_l in {"m", "male", "man"}:
		k = 0.9
		alpha = -0.411
		sex_corr = 1.0
	else:
		raise ValueError("sex must be 'male' or 'female'")

	x = scr_mg_dl / k
	gfr = 141.0 * (min(x, 1.0) ** alpha) * (max(x, 1.0) ** -1.209) * (0.993 ** age_yr)
	gfr *= sex_corr
	race_corr = 1.159 if is_black else 1.0
	gfr *= race_corr
	return EGFRResult(value_ml_min_1_73m2=gfr, sex_correction=sex_corr, race_correction=race_corr)


def pf_ratio(pao2_mmHg: float, fio2: float) -> float:
	"""Compute PaO₂/FiO₂ ratio.

	Args:
		pao2_mmHg: Arterial oxygen tension in mmHg
		fio2: Fraction of inspired oxygen (0–1)
	Returns:
		Dimensionless P/F ratio (mmHg)
	"""
	if fio2 <= 0:
		raise ValueError("FiO2 must be > 0")
	return pao2_mmHg / fio2


def oxygen_index(pao2_mmHg: float, fio2: float, map_cmH2O: float) -> float:
	"""Compute Oxygen Index (OI).

	OI = 100 × FiO2 × MAP / PaO2
	Units: PaO2 in mmHg, FiO2 fraction, MAP in cmH2O. Result is dimensionless.
	"""
	if pao2_mmHg <= 0:
		raise ValueError("PaO2 must be > 0")
	return 100.0 * fio2 * map_cmH2O / pao2_mmHg


@dataclass
class SixMWDResult:
	predicted_m: float
	lower_limit_normal_m: float


def six_minute_walk_distance(height_cm: float, weight_kg: float, age_yr: float, sex: str) -> SixMWDResult:
	"""Predict 6‑minute walk distance (6MWD) in meters.

	Enright & Sherrill reference equations:
	- Male:   6MWD = 7.57×height_cm − 5.02×age − 1.76×weight_kg − 309
	- Female: 6MWD = 2.11×height_cm − 5.78×age − 2.29×weight_kg + 667
	Lower limit of normal (LLN):
	- Male:   6MWD − 153
	- Female: 6MWD − 139
	"""
	sex_l = sex.strip().lower()
	if sex_l in {"m", "male", "man"}:
		mwd = 7.57 * height_cm - 5.02 * age_yr - 1.76 * weight_kg - 309.0
		lln = mwd - 153.0
	elif sex_l in {"f", "female", "woman"}:
		mwd = 2.11 * height_cm - 5.78 * age_yr - 2.29 * weight_kg + 667.0
		lln = mwd - 139.0
	else:
		raise ValueError("sex must be 'male' or 'female'")
	return SixMWDResult(predicted_m=mwd, lower_limit_normal_m=lln)


# Convenience collection for BSA comparisons

def compute_all_bsa(height_cm: float, weight_kg: float) -> Dict[str, float]:
	"""Return a dictionary with BSA values from all supported formulas (m²)."""
	values = {
		"Boyd": bsa_boyd(weight_kg),
		"DuBois": bsa_dubois(height_cm, weight_kg),
		"Haycock": bsa_haycock(height_cm, weight_kg),
		"Mosteller": bsa_mosteller(height_cm, weight_kg),
	}
	return values