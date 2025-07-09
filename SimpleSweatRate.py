# -*- coding: utf-8 -*-
"""
Sweat Rate Calculator for Exercise Physiology
Created on Tue Mar 28 18:59:57 2023
Updated for accuracy and usability

@author: Diego Malpica
Updated by: AI Assistant

Based on ACSM's Guidelines for Exercise Testing and Prescription
and current exercise physiology standards.
"""

import math

def calculate_sweat_rate(pre_weight_kg, post_weight_kg, fluid_intake_l, 
                        urine_volume_l, exercise_duration_hours):
    """
    Calculate sweat rate using the standard formula.
    
    Formula: Sweat Rate (L/h) = (Pre-exercise weight - Post-exercise weight + 
                                Fluid intake - Urine output) / Exercise duration
    
    Args:
        pre_weight_kg (float): Pre-exercise body weight in kg
        post_weight_kg (float): Post-exercise body weight in kg
        fluid_intake_l (float): Fluid intake during exercise in liters
        urine_volume_l (float): Urine volume during exercise in liters
        exercise_duration_hours (float): Exercise duration in hours
    
    Returns:
        float: Sweat rate in L/h
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if pre_weight_kg <= 0 or post_weight_kg <= 0:
        raise ValueError("Body weights must be positive values")
    
    if fluid_intake_l < 0 or urine_volume_l < 0:
        raise ValueError("Fluid intake and urine volume cannot be negative")
    
    if exercise_duration_hours <= 0:
        raise ValueError("Exercise duration must be positive")
    
    if abs(pre_weight_kg - post_weight_kg) > 5:
        raise ValueError("Weight change > 5kg seems unrealistic. Please check measurements.")
    
    # Calculate sweat rate
    weight_change_kg = pre_weight_kg - post_weight_kg
    total_fluid_loss_l = weight_change_kg + fluid_intake_l - urine_volume_l
    sweat_rate_lh = total_fluid_loss_l / exercise_duration_hours
    
    return sweat_rate_lh

def get_dehydration_percentage(pre_weight_kg, post_weight_kg):
    """
    Calculate percentage of body weight lost as dehydration.
    
    Args:
        pre_weight_kg (float): Pre-exercise weight in kg
        post_weight_kg (float): Post-exercise weight in kg
    
    Returns:
        float: Dehydration percentage
    """
    return ((pre_weight_kg - post_weight_kg) / pre_weight_kg) * 100

def interpret_sweat_rate(sweat_rate_lh):
    """
    Provide interpretation of sweat rate values.
    
    Args:
        sweat_rate_lh (float): Sweat rate in L/h
    
    Returns:
        str: Interpretation of sweat rate
    """
    if sweat_rate_lh < 0.5:
        return "Low sweat rate - typical for light exercise or cool conditions"
    elif sweat_rate_lh < 1.0:
        return "Moderate sweat rate - typical for moderate exercise"
    elif sweat_rate_lh < 2.0:
        return "High sweat rate - typical for intense exercise or hot conditions"
    elif sweat_rate_lh < 3.0:
        return "Very high sweat rate - monitor hydration closely"
    else:
        return "Extremely high sweat rate - validate measurements and consider medical consultation"

def interpret_dehydration(dehydration_percent):
    """
    Provide interpretation of dehydration level.
    
    Args:
        dehydration_percent (float): Dehydration as percentage of body weight
    
    Returns:
        str: Dehydration interpretation and recommendations
    """
    if dehydration_percent < 1:
        return "Minimal dehydration - good hydration maintained"
    elif dehydration_percent < 2:
        return "Mild dehydration - acceptable for most activities"
    elif dehydration_percent < 3:
        return "Moderate dehydration - increased risk of heat illness"
    elif dehydration_percent < 4:
        return "Significant dehydration - performance likely impaired"
    else:
        return "Severe dehydration - immediate rehydration needed, consider medical attention"

def calculate_replacement_fluid_needed(sweat_rate_lh, exercise_duration_hours, 
                                     current_intake_lh=0.0):
    """
    Calculate recommended fluid replacement rate.
    
    Args:
        sweat_rate_lh (float): Sweat rate in L/h
        exercise_duration_hours (float): Exercise duration in hours
        current_intake_lh (float): Current fluid intake rate in L/h
    
    Returns:
        tuple: (recommended_intake_lh, total_recommended_l)
    """
    # ACSM recommends replacing 150% of fluid lost for complete rehydration
    recommended_intake_lh = sweat_rate_lh * 1.5
    total_recommended_l = recommended_intake_lh * exercise_duration_hours
    
    return recommended_intake_lh, total_recommended_l

def get_user_input():
    """
    Get user input with validation.
    
    Returns:
        tuple: All validated input values
    """
    print("Sweat Rate Calculator")
    print("Enter measurements in the requested units:")
    print("-" * 40)
    
    while True:
        try:
            pre_weight = float(input("Pre-exercise body weight (kg): "))
            if pre_weight <= 0 or pre_weight > 300:
                print("Please enter a realistic body weight (0-300 kg)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            post_weight = float(input("Post-exercise body weight (kg): "))
            if post_weight <= 0 or post_weight > 300:
                print("Please enter a realistic body weight (0-300 kg)")
                continue
            if abs(pre_weight - post_weight) > 5:
                print("Weight change > 5kg seems unrealistic. Please verify measurements.")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            fluid_intake = float(input("Fluid intake during exercise (L): "))
            if fluid_intake < 0 or fluid_intake > 10:
                print("Please enter a realistic fluid intake (0-10 L)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            urine_volume = float(input("Urine volume during exercise (L): "))
            if urine_volume < 0 or urine_volume > 2:
                print("Please enter a realistic urine volume (0-2 L)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            duration = float(input("Exercise duration (hours): "))
            if duration <= 0 or duration > 24:
                print("Please enter a realistic exercise duration (0-24 hours)")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    return pre_weight, post_weight, fluid_intake, urine_volume, duration

def main():
    """Main function to run the sweat rate calculator."""
    try:
        pre_weight, post_weight, fluid_intake, urine_volume, duration = get_user_input()
        
        # Calculate sweat rate
        sweat_rate = calculate_sweat_rate(pre_weight, post_weight, fluid_intake, 
                                        urine_volume, duration)
        
        # Calculate dehydration percentage
        dehydration_pct = get_dehydration_percentage(pre_weight, post_weight)
        
        # Calculate fluid replacement recommendations
        recommended_rate, total_recommended = calculate_replacement_fluid_needed(
            sweat_rate, duration, fluid_intake/duration)
        
        # Display results
        print(f"\n{'='*50}")
        print(f"SWEAT RATE ANALYSIS RESULTS")
        print(f"{'='*50}")
        
        print(f"\nCalculated Values:")
        print(f"Sweat Rate: {sweat_rate:.2f} L/h")
        print(f"Dehydration: {dehydration_pct:.1f}% of body weight")
        print(f"Weight lost: {pre_weight - post_weight:.2f} kg")
        
        print(f"\nInterpretation:")
        print(f"Sweat rate: {interpret_sweat_rate(sweat_rate)}")
        print(f"Dehydration: {interpret_dehydration(dehydration_pct)}")
        
        print(f"\nRehydration Recommendations:")
        print(f"Recommended fluid intake rate: {recommended_rate:.2f} L/h")
        print(f"Total recommended intake: {total_recommended:.2f} L")
        
        if dehydration_pct > 2:
            print(f"\n⚠️  WARNING: Dehydration > 2% may impair performance and increase heat illness risk")
        
        if sweat_rate > 2.5:
            print(f"\n⚠️  WARNING: Very high sweat rate - monitor closely for heat illness symptoms")
        
        print(f"\nNote: These calculations are based on ACSM guidelines.")
        print(f"For medical or performance decisions, consult qualified professionals.")
        
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")

if __name__ == "__main__":
    main()