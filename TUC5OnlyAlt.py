# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 14:01:24 2023

@author: User
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# Load and preprocess the data
excel_file = r'C:\Users\User\OneDrive\FAC\Research\Hypoxia FAC\db.xlsx'
data = pd.read_excel(excel_file)
data = data[['altitude', 'PiO2', 'FiO2', 'SpO2', 'TUC']]

# Split the dataset into training and testing sets
X = data.drop('TUC', axis=1)
y = data['TUC']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define a function to evaluate model performance
def evaluate_model(y_test, y_pred):
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return mae, mse, r2

# Fine-tune hyperparameters using GridSearchCV
param_grid = {
    'learning_rate': [0.01, 0.1, 0.2],
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}
model = XGBRegressor(random_state=42)
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search.fit(X_train, y_train)

#Train a machine learning model using the best hyperparameters
best_params = grid_search.best_params_
model = XGBRegressor(**best_params, random_state=42)
model.fit(X_train, y_train)

#Evaluate the model using the testing set
y_pred = model.predict(X_test)
mae, mse, r2 = evaluate_model(y_test, y_pred)
print("Model Performance:")
print(f"Mean Absolute Error: {mae}")
print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")

#Use the trained model to predict TUC
def predict_tuc(altitude, PiO2, FiO2, SpO2, model):
    input_data = np.array([altitude, PiO2, FiO2, SpO2]).reshape(1, -1)
    return model.predict(input_data)
#using only altitude as a predictor
X_altitude = X[['altitude']]
X_train_alt, X_test_alt, y_train_alt, y_test_alt = train_test_split(X_altitude, y, test_size=0.2, random_state=42)

grid_search_alt = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search_alt.fit(X_train_alt, y_train_alt)

#Train a machine learning model using the best hyperparameters
best_params_alt = grid_search_alt.best_params_
model_alt = XGBRegressor(**best_params_alt, random_state=42)
model_alt.fit(X_train_alt, y_train_alt)

#Evaluate the model using the testing set
y_pred_alt = model_alt.predict(X_test_alt)
mae_alt, mse_alt, r2_alt = evaluate_model(y_test_alt, y_pred_alt)
print("\nModel Performance (Using Altitude Only):")
print(f"Mean Absolute Error: {mae_alt}")
print(f"Mean Squared Error: {mse_alt}")
print(f"R^2 Score: {r2_alt}")

#Use the trained model to predict TUC using only altitude
def predict_tuc_altitude_only(altitude, model):
    input_data = np.array([altitude]).reshape(1, -1)
    return model.predict(input_data)

#Example prediction using only altitude
altitude_only = 55000
predicted_tuc_altitude_only = predict_tuc_altitude_only(altitude_only, model_alt)
print(f"\nPredicted TUC for Altitude: {altitude_only} is {predicted_tuc_altitude_only[0]} minutes")
