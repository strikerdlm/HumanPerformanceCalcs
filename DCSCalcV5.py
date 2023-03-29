# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:07:45 2023

@author: Diego Malpica
"""

import pandas as pd
from joblib import load
from category_encoders import OneHotEncoder

def get_user_input():
    altitude = float(input("Enter altitude (ft): "))
    prebreathing_time = float(input("Enter prebreathing time (min): "))
    time_at_altitude = float(input("Enter time at altitude (min): "))
    exercise_level = input("Enter exercise level (Rest, Mild, Heavy): ")

    return altitude, prebreathing_time, time_at_altitude, exercise_level

def create_input_dataframe(user_input, onehot_encoder, column_names):
    altitude, prebreathing_time, time_at_altitude, exercise_level = user_input

    input_data = {'altitude': [altitude],
                  'prebreathing_time': [prebreathing_time],
                  'time_at_altitude': [time_at_altitude],
                  'exercise_level': [exercise_level]}

    input_df = pd.DataFrame(input_data)

    # One-hot encode the 'exercise_level' column
    exercise_level_encoded = onehot_encoder.transform(input_df[['exercise_level']])
    exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
    exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns)

    # Add the encoded columns to the input dataframe and remove the original 'exercise_level' column
    input_df = pd.concat([input_df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

    # Ensure the input dataframe has the same column order as the original dataframe
    input_df = input_df.reindex(columns=column_names)

    return input_df

def main():
# Load the trained model, OneHotEncoder, and column names
    model = load(r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\trained_model.joblib")
    onehot_encoder = load(r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\onehot_encoder.joblib")
    column_names = load(r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\column_names.joblib")

# Get user input
    user_input = get_user_input()

# Create input dataframe
    input_df = create_input_dataframe(user_input, onehot_encoder, column_names)

# Make a prediction
    risk_prediction = model.predict(input_df)
    risk_prediction = risk_prediction.clip(min=0, max=100)

    print(f"\nThe predicted risk of decompression sickness is {risk_prediction[0]:.2f}")


if __name__ == "__main__":
    main()