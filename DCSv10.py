# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 09:38:00 2023

@author: DiegoMalpica
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from joblib import dump

# Load the dataset from the Excel file
file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\data.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

# One-hot encode the 'exercise_level' column
onehot_encoder = OneHotEncoder(sparse_output=False)
exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)

# Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

# Split the data into input features (X) and target variable (y)
X = df.drop("risk_of_decompression_sickness", axis=1)
y = df["risk_of_decompression_sickness"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train an ensemble of Gradient Boosting Regressors
n_models = 1000
models = []

for i in range(n_models):
    model = GradientBoostingRegressor(n_estimators=100, random_state=i, learning_rate=0.1, max_depth=3)
    model.fit(X_train, y_train)
    models.append(model)

# Make predictions on the test set using the ensemble
y_preds = np.zeros((len(X_test), n_models))

for i, model in enumerate(models):
    y_preds[:, i] = model.predict(X_test)

y_pred_ensemble = y_preds.mean(axis=1)

# Ensure predictions are within a valid range (0 to 100)
y_pred_ensemble = y_pred_ensemble.clip(min=0, max=100)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred_ensemble)

print("Mean Squared Error (Ensemble):", mse)

# Calculate the R-squared
r2 = r2_score(y_test, y_pred_ensemble)
print("R-squared (Ensemble):", r2)

# Calculate the Mean Absolute Error
mae = mean_absolute_error(y_test, y_pred_ensemble)
print("Mean Absolute Error (Ensemble):", mae)

# Calculate the Root Mean Squared Error
rmse = np.sqrt(mse)
print("Root Mean Squared Error (Ensemble):", rmse)

# Print feature importances and intercept
print("Feature Importances:\n", model.feature_importances_)
print("Intercept:", model.init_.constant_[0][0])

# Add calculated risk to the original DataFrame using the ensemble
y_pred_all = np.zeros((len(df), n_models))

for i, model in enumerate(models):
    y_pred_all[:, i] = model.predict(df.drop("risk_of_decompression_sickness", axis=1))

df["calculated"] = y_pred_all.mean(axis=1).clip(min=0, max=100)

# Save the DataFrame to a new Excel file
output_file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\output_data_set.xlsx"
df.to_excel(output_file_path, sheet_name=sheet_name, engine="openpyxl", index=False)

# Save the trained model, OneHotEncoder, and column names
dump(model, r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\trained_model.joblib")
dump(onehot_encoder, r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\onehot_encoder.joblib")
dump(X.columns, r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\column_names.joblib")