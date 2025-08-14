# -*- coding: utf-8 -*-
"""
Time of Useful Consciousness (TUC) Predictor - Version 4
Created on Wed Mar 29 13:19:30 2023

@author: Diego Malpica

Machine learning-based TUC prediction using XGBoost.
Configurable file paths for improved portability.
"""

import pandas as pd
import numpy as np
import os
import argparse
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from joblib import dump


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load and validate the TUC dataset from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Loaded and validated dataframe
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    
    # Check for required columns
    required_columns = ['altitude', 'PiO2', 'FiO2', 'SpO2', 'TUC']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Select only required columns
    data = data[required_columns]
    
    # Check for missing values
    if data.isnull().any().any():
        print("Warning: Found missing values in data. Dropping rows with missing values.")
        data = data.dropna()
    
    print(f"Loaded {len(data)} records with columns: {list(data.columns)}")
    return data


def evaluate_model(y_test: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Evaluate model performance using multiple metrics.
    
    Args:
        y_test (np.ndarray): True values
        y_pred (np.ndarray): Predicted values
        
    Returns:
        dict: Dictionary containing evaluation metrics
    """
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    return {
        'mae': mae,
        'mse': mse,
        'r2': r2,
        'rmse': rmse
    }


def train_xgboost_model(X_train: pd.DataFrame, y_train: pd.Series, 
                       X_test: pd.DataFrame, y_test: pd.Series,
                       param_grid: dict = None, cv_folds: int = 5) -> tuple:
    """
    Train an XGBoost model with hyperparameter tuning.
    
    Args:
        X_train (pd.DataFrame): Training features
        y_train (pd.Series): Training targets
        X_test (pd.DataFrame): Test features
        y_test (pd.Series): Test targets
        param_grid (dict): Parameter grid for GridSearchCV
        cv_folds (int): Number of cross-validation folds
        
    Returns:
        tuple: (best_model, evaluation_metrics)
    """
    if param_grid is None:
        param_grid = {
            'learning_rate': [0.01, 0.1, 0.2],
            'n_estimators': [100, 200, 300],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0]
        }
    
    print("Starting hyperparameter tuning...")
    model = XGBRegressor(random_state=42)
    grid_search = GridSearchCV(
        estimator=model, 
        param_grid=param_grid, 
        cv=cv_folds, 
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    
    # Train final model with best parameters
    best_model = XGBRegressor(**grid_search.best_params_, random_state=42)
    best_model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = best_model.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    
    return best_model, metrics


def predict_tuc(altitude: float, PiO2: float, FiO2: float, SpO2: float, 
               model: XGBRegressor) -> float:
    """
    Predict TUC for given physiological parameters.
    
    Args:
        altitude (float): Altitude in feet
        PiO2 (float): Inspired oxygen pressure
        FiO2 (float): Fraction of inspired oxygen
        SpO2 (float): Oxygen saturation
        model (XGBRegressor): Trained model
        
    Returns:
        float: Predicted TUC in seconds
    """
    input_data = np.array([altitude, PiO2, FiO2, SpO2]).reshape(1, -1)
    prediction = model.predict(input_data)
    return float(prediction[0])


def save_model_and_results(model: XGBRegressor, metrics: dict, output_dir: str) -> None:
    """
    Save the trained model and performance metrics.
    
    Args:
        model (XGBRegressor): Trained model
        metrics (dict): Performance metrics
        output_dir (str): Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_file = output_path / "tuc_model.joblib"
    dump(model, model_file)
    print(f"Model saved to: {model_file}")
    
    # Save metrics
    metrics_file = output_path / "model_metrics.txt"
    with open(metrics_file, 'w') as f:
        f.write("TUC Model Performance Metrics\n")
        f.write("=" * 30 + "\n")
        for metric, value in metrics.items():
            f.write(f"{metric.upper()}: {value:.4f}\n")
    
    print(f"Metrics saved to: {metrics_file}")


def main():
    """Main function to run the TUC model training."""
    parser = argparse.ArgumentParser(description="TUC Prediction Model Training")
    parser.add_argument("--data_file", type=str,
                       default=os.getenv("TUC_DATA_FILE", "data/hypoxia_data.xlsx"),
                       help="Path to the input Excel file")
    parser.add_argument("--output_dir", type=str,
                       default=os.getenv("TUC_OUTPUT_DIR", "output"),
                       help="Output directory for model and results")
    parser.add_argument("--test_size", type=float, default=0.2,
                       help="Fraction of data to use for testing")
    parser.add_argument("--cv_folds", type=int, default=5,
                       help="Number of cross-validation folds")
    parser.add_argument("--random_state", type=int, default=42,
                       help="Random state for reproducibility")
    parser.add_argument("--predict", action="store_true",
                       help="Run interactive prediction mode")
    
    args = parser.parse_args()
    
    try:
        print("TUC Prediction Model Training")
        print("=" * 35)
        print(f"Data file: {args.data_file}")
        print(f"Output directory: {args.output_dir}")
        print()
        
        # Load and preprocess data
        print("Loading data...")
        data = load_data(args.data_file)
        
        # Split features and target
        X = data.drop('TUC', axis=1)
        y = data['TUC']
        
        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=args.random_state
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        print(f"Features: {list(X.columns)}")
        print()
        
        # Train model
        model, metrics = train_xgboost_model(X_train, y_train, X_test, y_test, cv_folds=args.cv_folds)
        
        # Display results
        print("Model Performance:")
        print(f"Mean Absolute Error: {metrics['mae']:.4f}")
        print(f"Mean Squared Error: {metrics['mse']:.4f}")
        print(f"Root Mean Squared Error: {metrics['rmse']:.4f}")
        print(f"R² Score: {metrics['r2']:.4f}")
        print()
        
        # Feature importance
        print("Feature Importances:")
        feature_names = X.columns
        importances = model.feature_importances_
        for name, importance in zip(feature_names, importances):
            print(f"{name}: {importance:.4f}")
        print()
        
        # Save model and results
        save_model_and_results(model, metrics, args.output_dir)
        
        # Interactive prediction mode
        if args.predict:
            print("Interactive Prediction Mode")
            print("-" * 25)
            while True:
                try:
                    print("\nEnter physiological parameters (or 'quit' to exit):")
                    altitude = input("Altitude (ft): ")
                    if altitude.lower() == 'quit':
                        break
                    
                    altitude = float(altitude)
                    PiO2 = float(input("Inspired O2 pressure (PiO2): "))
                    FiO2 = float(input("Fraction of inspired O2 (FiO2): "))
                    SpO2 = float(input("Oxygen saturation (SpO2): "))
                    
                    predicted_tuc = predict_tuc(altitude, PiO2, FiO2, SpO2, model)
                    
                    print(f"\nPredicted TUC: {predicted_tuc:.1f} seconds ({predicted_tuc/60:.1f} minutes)")
                    
                except ValueError as e:
                    print(f"Invalid input: {e}")
                except KeyboardInterrupt:
                    break
        
        print("Training completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

