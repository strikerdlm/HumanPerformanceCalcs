# -*- coding: utf-8 -*-
"""
Decompression Sickness (DCS) Risk Calculator
Created on Tue Mar 28 12:07:45 2023
Updated for portability and usability

@author: Diego Malpica
Updated by: AI Assistant

Machine learning-based DCS risk prediction for aerospace medicine.
Requires trained model files in the same directory or specified path.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def load_model_files(model_dir=None):
    """
    Load the trained model files with error handling.
    
    Args:
        model_dir (str, optional): Directory containing model files
    
    Returns:
        tuple: (model, onehot_encoder, column_names)
        
    Raises:
        FileNotFoundError: If model files are not found
        ImportError: If required libraries are not available
    """
    try:
        from joblib import load
        from category_encoders import OneHotEncoder
    except ImportError as e:
        raise ImportError(f"Required libraries not found: {e}. Install with: pip install joblib category-encoders")
    
    # Default model directory
    if model_dir is None:
        model_dir = Path(__file__).parent / "models"
    else:
        model_dir = Path(model_dir)
    
    # Model file paths
    model_files = {
        'model': model_dir / "trained_model.joblib",
        'encoder': model_dir / "onehot_encoder.joblib",
        'columns': model_dir / "column_names.joblib"
    }
    
    # Check if files exist
    missing_files = []
    for name, filepath in model_files.items():
        if not filepath.exists():
            missing_files.append(str(filepath))
    
    if missing_files:
        print("Missing model files:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nPlease ensure all model files are in the 'models' directory:")
        print("  - trained_model.joblib")
        print("  - onehot_encoder.joblib")
        print("  - column_names.joblib")
        raise FileNotFoundError("Required model files not found")
    
    # Load files
    try:
        model = load(model_files['model'])
        onehot_encoder = load(model_files['encoder'])
        column_names = load(model_files['columns'])
        
        print(f"Model files loaded successfully from: {model_dir}")
        return model, onehot_encoder, column_names
        
    except Exception as e:
        raise RuntimeError(f"Error loading model files: {e}")

def get_user_input():
    """
    Get user input with validation and error handling.
    
    Returns:
        tuple: (altitude, prebreathing_time, time_at_altitude, exercise_level)
    """
    print("DCS Risk Calculator")
    print("Enter mission parameters:")
    print("-" * 30)
    
    while True:
        try:
            altitude = float(input("Altitude (ft): "))
            if altitude < 0 or altitude > 100000:
                print("Please enter a realistic altitude (0-100,000 ft)")
                continue
            break
        except ValueError:
            print("Please enter a valid number for altitude")
    
    while True:
        try:
            prebreathing = float(input("Prebreathing time (min): "))
            if prebreathing < 0 or prebreathing > 300:
                print("Please enter a realistic prebreathing time (0-300 min)")
                continue
            break
        except ValueError:
            print("Please enter a valid number for prebreathing time")
    
    while True:
        try:
            time_alt = float(input("Time at altitude (min): "))
            if time_alt < 0 or time_alt > 1440:
                print("Please enter a realistic time at altitude (0-1440 min)")
                continue
            break
        except ValueError:
            print("Please enter a valid number for time at altitude")
    
    while True:
        exercise = input("Exercise level (Rest/Mild/Heavy): ").strip().title()
        if exercise in ['Rest', 'Mild', 'Heavy']:
            break
        print("Please enter 'Rest', 'Mild', or 'Heavy'")
    
    return altitude, prebreathing, time_alt, exercise

def create_input_dataframe(user_input, onehot_encoder, column_names):
    """
    Create input dataframe for model prediction.
    
    Args:
        user_input (tuple): User input values
        onehot_encoder: Trained OneHotEncoder
        column_names: Expected column names
    
    Returns:
        pd.DataFrame: Formatted input dataframe
    """
    altitude, prebreathing_time, time_at_altitude, exercise_level = user_input

    input_data = {
        'altitude': [altitude],
        'prebreathing_time': [prebreathing_time],
        'time_at_altitude': [time_at_altitude],
        'exercise_level': [exercise_level]
    }

    input_df = pd.DataFrame(input_data)

    # One-hot encode the exercise level
    try:
        exercise_level_encoded = onehot_encoder.transform(input_df[['exercise_level']])
        exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
        exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns)

        # Combine with other features
        input_df = pd.concat([input_df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

        # Ensure column order matches training data
        input_df = input_df.reindex(columns=column_names, fill_value=0)
        
        return input_df
        
    except Exception as e:
        raise RuntimeError(f"Error processing input data: {e}")

def interpret_dcs_risk(risk_percentage):
    """
    Interpret DCS risk percentage.
    
    Args:
        risk_percentage (float): DCS risk as percentage
    
    Returns:
        str: Risk interpretation
    """
    if risk_percentage < 1:
        return "Very low risk - routine precautions sufficient"
    elif risk_percentage < 5:
        return "Low risk - standard protocols recommended"
    elif risk_percentage < 15:
        return "Moderate risk - enhanced monitoring recommended"
    elif risk_percentage < 30:
        return "High risk - consider mission modification"
    else:
        return "Very high risk - mission not recommended without significant precautions"

def main():
    """Main function to run the DCS risk calculator."""
    try:
        # Load model files
        model, onehot_encoder, column_names = load_model_files()
        
        # Get user input
        user_input = get_user_input()
        
        # Create input dataframe
        input_df = create_input_dataframe(user_input, onehot_encoder, column_names)
        
        # Make prediction
        risk_prediction = model.predict(input_df)
        risk_percentage = float(risk_prediction[0])
        
        # Ensure risk is within valid range
        risk_percentage = max(0, min(100, risk_percentage))
        
        # Display results
        print(f"\n{'='*50}")
        print(f"DCS RISK ASSESSMENT RESULTS")
        print(f"{'='*50}")
        
        altitude, prebreathing_time, time_at_altitude, exercise_level = user_input
        
        print(f"\nMission Parameters:")
        print(f"Altitude: {altitude:,.0f} ft")
        print(f"Prebreathing time: {prebreathing_time:.0f} min")
        print(f"Time at altitude: {time_at_altitude:.0f} min")
        print(f"Exercise level: {exercise_level}")
        
        print(f"\nPredicted DCS Risk: {risk_percentage:.1f}%")
        print(f"Risk Assessment: {interpret_dcs_risk(risk_percentage)}")
        
        # Safety warnings
        if risk_percentage > 15:
            print(f"\n⚠️  WARNING: Elevated DCS risk - consider mission modification")
        if altitude > 25000:
            print(f"⚠️  WARNING: Very high altitude - ensure adequate life support")
        if prebreathing_time < 30 and altitude > 18000:
            print(f"⚠️  WARNING: Limited prebreathing at high altitude increases risk")
        
        print(f"\nNote: This is a predictive model for research purposes.")
        print(f"For operational decisions, consult qualified flight surgeons.")
        
    except (FileNotFoundError, ImportError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Input error: {e}")
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()