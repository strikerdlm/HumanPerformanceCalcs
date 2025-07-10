# -*- coding: utf-8 -*-
"""
Predicted Heat Strain using Heart Rate (PHS-HR) Model
Created on Wed Mar 29 07:54:25 2023
Updated for completeness and accuracy

@author: User
Updated by: AI Assistant

Based on:
- ISO 7933:2004 Ergonomics of the thermal environment
- Malchaire, J. (2006). Predicted heat strain model
- Occupational heat stress assessment standards

The PHS-HR model predicts physiological strain under heat stress conditions
using heart rate as a key indicator.
"""

import math

class PHSHRModel:
    """
    Predicted Heat Strain using Heart Rate (PHS-HR) Model implementation.
    
    This model estimates heat strain based on environmental conditions,
    personal factors, and heart rate response.
    """
    
    def __init__(self):
        """Initialize the PHS-HR model with default constants."""
        # Physical constants
        self.delta_Hv = 2454  # Latent heat of vaporization (kJ/kg)
        self.cp_air = 1.005   # Specific heat of air (kJ/kg·K)
        self.sigma = 5.67e-8  # Stefan-Boltzmann constant (W/m²·K⁴)
        
        # Physiological constants
        self.body_surface_area = 1.8  # m² (average adult)
        self.specific_heat_body = 3.5  # kJ/kg·K
        
    def validate_inputs(self, ta, tr, pa, va, hr, hr0, icl, age, weight):
        """
        Validate all input parameters.
        
        Args:
            ta (float): Air temperature (°C)
            tr (float): Radiant temperature (°C)
            pa (float): Water vapor pressure (kPa)
            va (float): Air velocity (m/s)
            hr (float): Current heart rate (bpm)
            hr0 (float): Resting heart rate (bpm)
            icl (float): Clothing insulation (clo)
            age (int): Age (years)
            weight (float): Body weight (kg)
        
        Raises:
            ValueError: If inputs are outside valid ranges
        """
        if not (0 <= ta <= 60):
            raise ValueError("Air temperature must be between 0-60°C")
        
        if not (0 <= tr <= 80):
            raise ValueError("Radiant temperature must be between 0-80°C")
        
        if not (0 <= pa <= 10):
            raise ValueError("Water vapor pressure must be between 0-10 kPa")
        
        if not (0 <= va <= 5):
            raise ValueError("Air velocity must be between 0-5 m/s")
        
        if not (50 <= hr <= 200):
            raise ValueError("Heart rate must be between 50-200 bpm")
        
        if not (40 <= hr0 <= 100):
            raise ValueError("Resting heart rate must be between 40-100 bpm")
        
        if not (0 <= icl <= 3):
            raise ValueError("Clothing insulation must be between 0-3 clo")
        
        if not (18 <= age <= 70):
            raise ValueError("Age must be between 18-70 years")
        
        if not (40 <= weight <= 150):
            raise ValueError("Weight must be between 40-150 kg")
    
    def calculate_convective_heat_transfer_coefficient(self, va):
        """
        Calculate convective heat transfer coefficient.
        
        Args:
            va (float): Air velocity (m/s)
        
        Returns:
            float: Convective heat transfer coefficient (W/m²·K)
        """
        return 8.3 * (va ** 0.6)
    
    def calculate_evaporative_heat_transfer_coefficient(self, hc):
        """
        Calculate evaporative heat transfer coefficient.
        
        Args:
            hc (float): Convective heat transfer coefficient (W/m²·K)
        
        Returns:
            float: Evaporative heat transfer coefficient (W/m²·kPa)
        """
        return 16.5 * hc
    
    def calculate_metabolic_rate(self, hr, hr0, age, weight):
        """
        Calculate metabolic rate based on heart rate response.
        
        Args:
            hr (float): Current heart rate (bpm)
            hr0 (float): Resting heart rate (bpm)
            age (int): Age (years)
            weight (float): Weight (kg)
        
        Returns:
            float: Metabolic rate (W/m²)
        """
        # Base metabolic rate (W/m²)
        m0 = 58.2  # Resting metabolic rate
        
        # Maximum heart rate
        hr_max = 220 - age
        
        # Heart rate reserve
        hr_reserve = hr_max - hr0
        
        # Metabolic rate calculation
        if hr <= hr0:
            return m0
        
        # Metabolic rate increases with heart rate
        hr_ratio = (hr - hr0) / hr_reserve
        metabolic_rate = m0 + (hr_ratio * (300 - m0))  # Max ~300 W/m² for heavy work
        
        return min(metabolic_rate, 400)  # Cap at 400 W/m²
    
    def calculate_clothing_factors(self, icl, va):
        """
        Calculate clothing thermal resistance and permeability factors.
        
        Args:
            icl (float): Clothing insulation (clo)
            va (float): Air velocity (m/s)
        
        Returns:
            tuple: (thermal_resistance, permeability_factor)
        """
        # Convert clo to m²·K/W
        thermal_resistance = icl * 0.155
        
        # Clothing permeability factor (simplified)
        permeability_factor = 0.45 + 0.55 * math.exp(-0.3 * icl)
        
        return thermal_resistance, permeability_factor
    
    def calculate_heat_exchanges(self, ta, tr, pa, va, hr, hr0, icl, age, weight, tsk=35.0):
        """
        Calculate various heat exchange components.
        
        Args:
            ta (float): Air temperature (°C)
            tr (float): Radiant temperature (°C)
            pa (float): Water vapor pressure (kPa)
            va (float): Air velocity (m/s)
            hr (float): Current heart rate (bpm)
            hr0 (float): Resting heart rate (bpm)
            icl (float): Clothing insulation (clo)
            age (int): Age (years)
            weight (float): Weight (kg)
            tsk (float): Skin temperature (°C)
        
        Returns:
            dict: Heat exchange components
        """
        # Calculate heat transfer coefficients
        hc = self.calculate_convective_heat_transfer_coefficient(va)
        he = self.calculate_evaporative_heat_transfer_coefficient(hc)
        
        # Calculate metabolic rate
        M = self.calculate_metabolic_rate(hr, hr0, age, weight)
        
        # Calculate clothing factors
        thermal_resistance, permeability_factor = self.calculate_clothing_factors(icl, va)
        
        # Convective heat exchange (W/m²)
        C = hc * (tsk - ta) / (1 + hc * thermal_resistance)
        
        # Radiative heat exchange (W/m²)
        # Simplified linear approximation
        hr_rad = 4 * self.sigma * ((tr + 273.15) ** 3) / (1 + thermal_resistance * 4 * self.sigma * ((tr + 273.15) ** 3))
        R = hr_rad * (tsk - tr)
        
        # Required evaporative heat loss (W/m²)
        E_req = M - C - R
        
        # Maximum evaporative heat loss (W/m²)
        # Saturated vapor pressure at skin temperature
        psk_sat = 0.6105 * math.exp(17.27 * tsk / (tsk + 237.3))
        E_max = he * (psk_sat - pa) * permeability_factor
        
        # Actual evaporative heat loss
        E_act = min(E_req, E_max)
        
        # Heat storage (W/m²)
        S = M - C - R - E_act
        
        return {
            'metabolic_rate': M,
            'convective': C,
            'radiative': R,
            'evaporative_required': E_req,
            'evaporative_max': E_max,
            'evaporative_actual': E_act,
            'heat_storage': S,
            'skin_temperature': tsk
        }
    
    def predict_heat_strain(self, ta, tr, pa, va, hr, hr0, icl, age, weight, duration_min=60):
        """
        Predict heat strain using the PHS-HR model.
        
        Args:
            ta (float): Air temperature (°C)
            tr (float): Radiant temperature (°C)
            pa (float): Water vapor pressure (kPa)
            va (float): Air velocity (m/s)
            hr (float): Current heart rate (bpm)
            hr0 (float): Resting heart rate (bpm)
            icl (float): Clothing insulation (clo)
            age (int): Age (years)
            weight (float): Weight (kg)
            duration_min (int): Exposure duration (minutes)
        
        Returns:
            dict: Heat strain prediction results
        """
        # Validate inputs
        self.validate_inputs(ta, tr, pa, va, hr, hr0, icl, age, weight)
        
        # Calculate heat exchanges
        heat_exchanges = self.calculate_heat_exchanges(ta, tr, pa, va, hr, hr0, icl, age, weight)
        
        # Predict core temperature rise
        # Simplified model: ΔTcore = S * time / (body_mass * specific_heat)
        body_mass = weight
        delta_t_core = (heat_exchanges['heat_storage'] * duration_min * 60) / (body_mass * self.specific_heat_body * 1000)
        
        # Predict final core temperature
        initial_core_temp = 37.0  # Normal core temperature
        final_core_temp = initial_core_temp + delta_t_core
        
        # Calculate heat strain indicators
        hr_strain = (hr - hr0) / (220 - age - hr0)  # Normalized heart rate strain
        
        # Predict sweat rate (L/h)
        sweat_rate = max(0, heat_exchanges['evaporative_actual'] / self.delta_Hv)
        
        # Overall heat strain index (0-10 scale)
        heat_strain_index = min(10, max(0, 
            5 * ((final_core_temp - 37) / 2) + 5 * hr_strain))
        
        return {
            'heat_exchanges': heat_exchanges,
            'core_temperature_rise': delta_t_core,
            'predicted_core_temperature': final_core_temp,
            'heart_rate_strain': hr_strain,
            'predicted_sweat_rate': sweat_rate,
            'heat_strain_index': heat_strain_index,
            'duration_minutes': duration_min
        }
    
    def interpret_results(self, results):
        """
        Interpret heat strain prediction results.
        
        Args:
            results (dict): Results from predict_heat_strain()
        
        Returns:
            dict: Interpreted results with recommendations
        """
        core_temp = results['predicted_core_temperature']
        strain_index = results['heat_strain_index']
        sweat_rate = results['predicted_sweat_rate']
        
        # Core temperature interpretation
        if core_temp < 37.5:
            temp_risk = "Low risk - core temperature within normal range"
        elif core_temp < 38.0:
            temp_risk = "Moderate risk - mild hyperthermia developing"
        elif core_temp < 38.5:
            temp_risk = "High risk - significant hyperthermia"
        else:
            temp_risk = "Very high risk - dangerous hyperthermia"
        
        # Heat strain index interpretation
        if strain_index < 2:
            strain_risk = "Low heat strain - minimal physiological stress"
        elif strain_index < 4:
            strain_risk = "Moderate heat strain - monitor for symptoms"
        elif strain_index < 6:
            strain_risk = "High heat strain - implement cooling measures"
        else:
            strain_risk = "Very high heat strain - immediate intervention required"
        
        # Sweat rate interpretation
        if sweat_rate < 0.5:
            sweat_risk = "Low sweat rate - adequate for conditions"
        elif sweat_rate < 1.0:
            sweat_risk = "Moderate sweat rate - ensure adequate hydration"
        elif sweat_rate < 1.5:
            sweat_risk = "High sweat rate - aggressive hydration needed"
        else:
            sweat_risk = "Very high sweat rate - risk of dehydration"
        
        return {
            'core_temperature_risk': temp_risk,
            'heat_strain_risk': strain_risk,
            'sweat_rate_risk': sweat_risk,
            'overall_assessment': strain_risk,
            'recommendations': self.generate_recommendations(results)
        }
    
    def generate_recommendations(self, results):
        """
        Generate specific recommendations based on results.
        
        Args:
            results (dict): Results from predict_heat_strain()
        
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        core_temp = results['predicted_core_temperature']
        strain_index = results['heat_strain_index']
        sweat_rate = results['predicted_sweat_rate']
        
        if core_temp > 38.0:
            recommendations.append("Implement active cooling measures immediately")
        
        if strain_index > 4:
            recommendations.append("Reduce work intensity or duration")
            recommendations.append("Increase rest periods in cool environment")
        
        if sweat_rate > 1.0:
            recommendations.append("Ensure fluid replacement rate of at least {:.1f} L/h".format(sweat_rate * 1.5))
        
        if results['heat_exchanges']['evaporative_required'] > results['heat_exchanges']['evaporative_max']:
            recommendations.append("Consider lighter, more breathable clothing")
            recommendations.append("Increase air movement if possible")
        
        return recommendations

def get_user_input():
    """
    Get user input with validation.
    
    Returns:
        dict: All validated input parameters
    """
    print("PHS-HR Heat Strain Prediction Model")
    print("Enter environmental and personal parameters:")
    print("-" * 45)
    
    inputs = {}
    
    # Environmental parameters
    while True:
        try:
            inputs['ta'] = float(input("Air temperature (°C): "))
            if 0 <= inputs['ta'] <= 60:
                break
            print("Please enter a temperature between 0-60°C")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['tr'] = float(input("Radiant temperature (°C): "))
            if 0 <= inputs['tr'] <= 80:
                break
            print("Please enter a temperature between 0-80°C")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['pa'] = float(input("Water vapor pressure (kPa): "))
            if 0 <= inputs['pa'] <= 10:
                break
            print("Please enter a pressure between 0-10 kPa")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['va'] = float(input("Air velocity (m/s): "))
            if 0 <= inputs['va'] <= 5:
                break
            print("Please enter a velocity between 0-5 m/s")
        except ValueError:
            print("Please enter a valid number")
    
    # Personal parameters
    while True:
        try:
            inputs['hr'] = float(input("Current heart rate (bpm): "))
            if 50 <= inputs['hr'] <= 200:
                break
            print("Please enter a heart rate between 50-200 bpm")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['hr0'] = float(input("Resting heart rate (bpm): "))
            if 40 <= inputs['hr0'] <= 100:
                break
            print("Please enter a resting heart rate between 40-100 bpm")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['icl'] = float(input("Clothing insulation (clo): "))
            if 0 <= inputs['icl'] <= 3:
                break
            print("Please enter clothing insulation between 0-3 clo")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['age'] = int(input("Age (years): "))
            if 18 <= inputs['age'] <= 70:
                break
            print("Please enter age between 18-70 years")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['weight'] = float(input("Body weight (kg): "))
            if 40 <= inputs['weight'] <= 150:
                break
            print("Please enter weight between 40-150 kg")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            inputs['duration'] = int(input("Exposure duration (minutes): "))
            if 1 <= inputs['duration'] <= 480:
                break
            print("Please enter duration between 1-480 minutes")
        except ValueError:
            print("Please enter a valid number")
    
    return inputs

def main():
    """Main function to run the PHS-HR model."""
    try:
        # Get user input
        inputs = get_user_input()
        
        # Create model instance
        model = PHSHRModel()
        
        # Predict heat strain
        results = model.predict_heat_strain(
            inputs['ta'], inputs['tr'], inputs['pa'], inputs['va'],
            inputs['hr'], inputs['hr0'], inputs['icl'],
            inputs['age'], inputs['weight'], inputs['duration']
        )
        
        # Interpret results
        interpretation = model.interpret_results(results)
        
        # Display results
        print(f"\n{'='*60}")
        print(f"PHS-HR HEAT STRAIN PREDICTION RESULTS")
        print(f"{'='*60}")
        
        print(f"\nInput Parameters:")
        print(f"Air temperature: {inputs['ta']:.1f}°C")
        print(f"Radiant temperature: {inputs['tr']:.1f}°C")
        print(f"Water vapor pressure: {inputs['pa']:.1f} kPa")
        print(f"Air velocity: {inputs['va']:.1f} m/s")
        print(f"Current heart rate: {inputs['hr']:.0f} bpm")
        print(f"Resting heart rate: {inputs['hr0']:.0f} bpm")
        print(f"Clothing insulation: {inputs['icl']:.1f} clo")
        print(f"Age: {inputs['age']} years")
        print(f"Weight: {inputs['weight']:.1f} kg")
        print(f"Duration: {inputs['duration']} minutes")
        
        print(f"\nHeat Exchange Analysis:")
        he = results['heat_exchanges']
        print(f"Metabolic rate: {he['metabolic_rate']:.1f} W/m²")
        print(f"Convective heat loss: {he['convective']:.1f} W/m²")
        print(f"Radiative heat loss: {he['radiative']:.1f} W/m²")
        print(f"Required evaporative loss: {he['evaporative_required']:.1f} W/m²")
        print(f"Maximum evaporative loss: {he['evaporative_max']:.1f} W/m²")
        print(f"Actual evaporative loss: {he['evaporative_actual']:.1f} W/m²")
        print(f"Heat storage: {he['heat_storage']:.1f} W/m²")
        
        print(f"\nHeat Strain Predictions:")
        print(f"Core temperature rise: {results['core_temperature_rise']:.2f}°C")
        print(f"Predicted core temperature: {results['predicted_core_temperature']:.2f}°C")
        print(f"Heart rate strain: {results['heart_rate_strain']:.2f}")
        print(f"Predicted sweat rate: {results['predicted_sweat_rate']:.2f} L/h")
        print(f"Heat strain index: {results['heat_strain_index']:.2f}")
        
        print(f"\nRisk Assessment:")
        print(f"Core temperature: {interpretation['core_temperature_risk']}")
        print(f"Heat strain: {interpretation['heat_strain_risk']}")
        print(f"Sweat rate: {interpretation['sweat_rate_risk']}")
        
        if interpretation['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(interpretation['recommendations'], 1):
                print(f"{i}. {rec}")
        
        # Safety warnings
        if results['predicted_core_temperature'] > 38.0:
            print(f"\n⚠️  WARNING: Predicted core temperature > 38°C indicates heat strain")
        if results['heat_strain_index'] > 6:
            print(f"⚠️  WARNING: High heat strain index indicates dangerous conditions")
        if results['predicted_sweat_rate'] > 1.5:
            print(f"⚠️  WARNING: Very high sweat rate - risk of severe dehydration")
        
        print(f"\nNote: This model is for research and educational purposes.")
        print(f"For operational decisions, consult qualified professionals.")
        
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"Calculation error: {e}")

if __name__ == "__main__":
    main()




