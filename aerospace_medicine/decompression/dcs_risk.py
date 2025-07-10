# -*- coding: utf-8 -*-
"""
Decompression Sickness (DCS) Risk Calculator
Created on Tue Mar 28 12:07:45 2023
Updated for portability and usability

@author: Diego Malpica

Machine learning-based DCS risk prediction for aerospace medicine.
Requires trained model files in the same directory or specified path.
"""

import pandas as pd
import os
import sys
from pathlib import Path
from calculators.utils import get_float_input

def load_model_files(model_dir: str = None) -> tuple:
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
    
    # Default model directory - look for models in project root
    if model_dir is None:
        model_dir = Path(__file__).parent.parent.parent / "models" / "dcs"
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
        print("\nPlease ensure all model files are in the 'models/dcs' directory:")
        print("  - trained_model.joblib")
        print("  - onehot_encoder.joblib")
        print("  - column_names.joblib")
        raise FileNotFoundError("Required model files not found")
    
    # Load the models
    try:
        model = load(model_files['model'])
        onehot_encoder = load(model_files['encoder'])
        column_names = load(model_files['columns'])
        return model, onehot_encoder, column_names
    except Exception as e:
        raise RuntimeError(f"Error loading model files: {e}")

def get_user_input() -> tuple:
    """
    Get user input with validation and error handling.
    
    Returns:
        tuple: (altitude, prebreathing_time, time_at_altitude, exercise_level)
    """
    print("DCS Risk Calculator")
    print("For research and educational use only. Not for operational or clinical decision-making.")
    print("Enter mission parameters:")
    print("-" * 30)
    
    altitude = get_float_input("Altitude (ft): ", min_value=0, max_value=100000)
    prebreathing = get_float_input("Prebreathing time (min): ", min_value=0, max_value=300)
    time_alt = get_float_input("Time at altitude (min): ", min_value=0, max_value=1440)
    
    while True:
        exercise = input("Exercise level (Rest/Mild/Heavy): ").strip().title()
        if exercise in ['Rest', 'Mild', 'Heavy']:
            break
        print("Please enter 'Rest', 'Mild', or 'Heavy'")
    
    return altitude, prebreathing, time_alt, exercise

def create_input_dataframe(user_input: tuple, onehot_encoder, column_names) -> pd.DataFrame:
    """
    Create a properly formatted DataFrame for model prediction.
    
    Args:
        user_input (tuple): User input values
        onehot_encoder: Trained one-hot encoder
        column_names: Expected column names for the model
    
    Returns:
        pd.DataFrame: Formatted input dataframe
    """
    altitude, prebreathing_time, time_at_altitude, exercise_level = user_input
    
    # Create initial dataframe
    input_data = {
        'Altitude': [altitude],
        'Prebreathing_Time': [prebreathing_time],
        'Time_at_Altitude': [time_at_altitude],
        'Exercise_Level': [exercise_level]
    }
    
    input_df = pd.DataFrame(input_data)
    
    # Apply one-hot encoding to categorical variables
    categorical_columns = input_df.select_dtypes(include=['object']).columns
    if len(categorical_columns) > 0:
        encoded_categorical = onehot_encoder.transform(input_df[categorical_columns])
        
        # Remove original categorical columns and add encoded ones
        input_df = input_df.drop(columns=categorical_columns)
        input_df = pd.concat([input_df, encoded_categorical], axis=1)
    
    # Ensure all expected columns are present
    for col in column_names:
        if col not in input_df.columns:
            input_df[col] = 0
    
    # Reorder columns to match training data
    input_df = input_df[column_names]
    
    return input_df

def interpret_dcs_risk(risk_percentage: float) -> str:
    """
    Interpret the DCS risk percentage.
    
    Args:
        risk_percentage (float): Predicted risk percentage
    
    Returns:
        str: Risk interpretation
    """
    if risk_percentage < 2:
        return "Very Low Risk - Standard precautions recommended"
    elif risk_percentage < 5:
        return "Low Risk - Monitor for symptoms"
    elif risk_percentage < 15:
        return "Moderate Risk - Enhanced monitoring recommended"
    elif risk_percentage < 30:
        return "High Risk - Consider mission modification"
    else:
        return "Very High Risk - Mission modification strongly recommended"

def main() -> None:
    """
    Main function to run the DCS risk calculator.
    """
    try:
        print("\nDecompression Sickness (DCS) Risk Calculator")
        print("For research and educational use only. Not for operational or clinical decision-making.")
        print("-" * 70)
        
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
    except KeyboardInterrupt:
        print("\nCalculation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 