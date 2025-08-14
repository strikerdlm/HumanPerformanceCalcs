# -*- coding: utf-8 -*-
"""
Enhanced DCS Risk Model (Version 10)
Created on Sat Mar 25 09:38:00 2023

@author: DiegoMalpica

Machine learning ensemble model for DCS risk prediction.
Configurable file paths for improved portability.
"""

import pandas as pd
import numpy as np
import os
import argparse
from pathlib import Path
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from joblib import dump


def load_data(file_path: str, sheet_name: str = "data") -> pd.DataFrame:
    """
    Load and preprocess the dataset from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        sheet_name (str): Name of the sheet to load
        
    Returns:
        pd.DataFrame: Processed dataframe
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the required columns are missing
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
    
    # Check for required columns
    required_columns = ['exercise_level', 'risk_of_decompression_sickness']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for missing values and handle them accordingly
    df.dropna(inplace=True)
    
    return df


def preprocess_data(df: pd.DataFrame) -> tuple[pd.DataFrame, OneHotEncoder]:
    """
    Preprocess the data including one-hot encoding.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        tuple: (processed_dataframe, onehot_encoder)
    """
    # One-hot encode the 'exercise_level' column
    onehot_encoder = OneHotEncoder(sparse_output=False)
    exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
    exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
    exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)

    # Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
    df_processed = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)
    
    return df_processed, onehot_encoder


def train_ensemble_model(X_train: pd.DataFrame, y_train: pd.Series, n_models: int = 1000) -> list:
    """
    Train an ensemble of Gradient Boosting Regressors.
    
    Args:
        X_train (pd.DataFrame): Training features
        y_train (pd.Series): Training targets
        n_models (int): Number of models in the ensemble
        
    Returns:
        list: List of trained models
    """
    models = []
    
    print(f"Training ensemble of {n_models} models...")
    for i in range(n_models):
        if (i + 1) % 100 == 0:
            print(f"Training model {i + 1}/{n_models}")
            
        model = GradientBoostingRegressor(
            n_estimators=100, 
            random_state=i, 
            learning_rate=0.1, 
            max_depth=3
        )
        model.fit(X_train, y_train)
        models.append(model)
    
    return models


def evaluate_ensemble(models: list, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Evaluate the ensemble model performance.
    
    Args:
        models (list): List of trained models
        X_test (pd.DataFrame): Test features
        y_test (pd.Series): Test targets
        
    Returns:
        dict: Performance metrics
    """
    # Make predictions on the test set using the ensemble
    y_preds = np.zeros((len(X_test), len(models)))

    for i, model in enumerate(models):
        y_preds[:, i] = model.predict(X_test)

    y_pred_ensemble = y_preds.mean(axis=1)

    # Ensure predictions are within a valid range (0 to 100)
    y_pred_ensemble = y_pred_ensemble.clip(min=0, max=100)

    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred_ensemble)
    r2 = r2_score(y_test, y_pred_ensemble)
    mae = mean_absolute_error(y_test, y_pred_ensemble)
    rmse = np.sqrt(mse)
    
    return {
        'mse': mse,
        'r2': r2,
        'mae': mae,
        'rmse': rmse,
        'predictions': y_pred_ensemble
    }


def save_results(df: pd.DataFrame, models: list, onehot_encoder: OneHotEncoder, 
                output_dir: str, predictions: np.ndarray) -> None:
    """
    Save the results and trained models.
    
    Args:
        df (pd.DataFrame): Original dataframe
        models (list): Trained models
        onehot_encoder (OneHotEncoder): Fitted encoder
        output_dir (str): Output directory
        predictions (np.ndarray): Model predictions
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Add predictions to dataframe
    df_with_predictions = df.copy()
    
    # Make predictions for all data
    X_all = df.drop("risk_of_decompression_sickness", axis=1)
    y_pred_all = np.zeros((len(df), len(models)))

    for i, model in enumerate(models):
        y_pred_all[:, i] = model.predict(X_all)

    df_with_predictions["calculated"] = y_pred_all.mean(axis=1).clip(min=0, max=100)

    # Save results
    output_file = output_path / "output_data_set.xlsx"
    df_with_predictions.to_excel(output_file, sheet_name="data", engine="openpyxl", index=False)
    print(f"Results saved to: {output_file}")

    # Save models
    model_file = output_path / "trained_model.joblib"
    encoder_file = output_path / "onehot_encoder.joblib"
    columns_file = output_path / "column_names.joblib"
    
    dump(models[-1], model_file)  # Save the last model as representative
    dump(onehot_encoder, encoder_file)
    dump(X_all.columns.tolist(), columns_file)
    
    print(f"Models saved to: {output_path}")


def main():
    """Main function to run the DCS ensemble model training."""
    parser = argparse.ArgumentParser(description="DCS Risk Ensemble Model Training")
    parser.add_argument("--data_file", type=str, 
                       default=os.getenv("DCS_DATA_FILE", "data/dcs_data.xlsx"),
                       help="Path to the input Excel file")
    parser.add_argument("--sheet_name", type=str, default="data",
                       help="Name of the Excel sheet to load")
    parser.add_argument("--output_dir", type=str,
                       default=os.getenv("DCS_OUTPUT_DIR", "output"),
                       help="Output directory for results and models")
    parser.add_argument("--n_models", type=int, default=1000,
                       help="Number of models in the ensemble")
    parser.add_argument("--test_size", type=float, default=0.2,
                       help="Fraction of data to use for testing")
    parser.add_argument("--random_state", type=int, default=42,
                       help="Random state for reproducibility")
    
    args = parser.parse_args()
    
    try:
        print("DCS Ensemble Model Training")
        print("=" * 40)
        print(f"Data file: {args.data_file}")
        print(f"Output directory: {args.output_dir}")
        print(f"Number of models: {args.n_models}")
        print()
        
        # Load and preprocess data
        print("Loading data...")
        df = load_data(args.data_file, args.sheet_name)
        print(f"Loaded {len(df)} records")
        
        print("Preprocessing data...")
        df_processed, onehot_encoder = preprocess_data(df)
        
        # Split the data
        X = df_processed.drop("risk_of_decompression_sickness", axis=1)
        y = df_processed["risk_of_decompression_sickness"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=args.random_state
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        print()
        
        # Train ensemble
        models = train_ensemble_model(X_train, y_train, args.n_models)
        
        # Evaluate model
        print("Evaluating ensemble...")
        results = evaluate_ensemble(models, X_test, y_test)
        
        print("Model Performance:")
        print(f"Mean Squared Error: {results['mse']:.4f}")
        print(f"R-squared: {results['r2']:.4f}")
        print(f"Mean Absolute Error: {results['mae']:.4f}")
        print(f"Root Mean Squared Error: {results['rmse']:.4f}")
        print()
        
        # Print feature importances
        print("Feature Importances:")
        feature_names = X.columns
        importances = models[-1].feature_importances_
        for name, importance in zip(feature_names, importances):
            print(f"{name}: {importance:.4f}")
        print()
        
        # Save results
        print("Saving results...")
        save_results(df_processed, models, onehot_encoder, args.output_dir, results['predictions'])
        
        print("Training completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())