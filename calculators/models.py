# -*- coding: utf-8 -*-
"""
Model Management Utilities for Human Performance Calculations

This module provides standardized functions for saving and loading machine learning models
across all calculators in the project. It ensures consistent model handling, proper error
handling, and clear documentation of expected file locations.

@author: Diego Malpica
"""

import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    warnings.warn("joblib not available. Some model formats may not be supported.")


class ModelManager:
    """
    Centralized model management for consistent saving/loading across the project.
    
    Supports both joblib (preferred) and pickle formats with automatic format detection.
    Provides standardized directory structure and file naming conventions.
    """
    
    def __init__(self, base_dir: Union[str, Path] = "models"):
        """
        Initialize the ModelManager.
        
        Args:
            base_dir (Union[str, Path]): Base directory for model storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard file extensions
        self.joblib_ext = ".joblib"
        self.pickle_ext = ".pkl"
        
        # Preferred format
        self.preferred_format = "joblib" if JOBLIB_AVAILABLE else "pickle"
    
    def save_model(self, model: Any, model_name: str, 
                   model_type: str = "general", 
                   format_type: str = "auto",
                   metadata: Optional[Dict] = None) -> Path:
        """
        Save a model with standardized naming and location.
        
        Args:
            model (Any): The model object to save
            model_name (str): Name of the model (e.g., "dcs_risk", "tuc_predictor")
            model_type (str): Type/category of model (e.g., "regression", "classification")
            format_type (str): Format to use ("joblib", "pickle", or "auto")
            metadata (Optional[Dict]): Additional metadata to save alongside model
            
        Returns:
            Path: Path to the saved model file
            
        Raises:
            ValueError: If format is not supported
            IOError: If saving fails
        """
        # Determine format
        if format_type == "auto":
            format_type = self.preferred_format
        
        if format_type not in ["joblib", "pickle"]:
            raise ValueError(f"Unsupported format: {format_type}. Use 'joblib' or 'pickle'.")
        
        if format_type == "joblib" and not JOBLIB_AVAILABLE:
            warnings.warn("joblib not available, falling back to pickle")
            format_type = "pickle"
        
        # Create model directory
        model_dir = self.base_dir / model_type / model_name
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension and save function
        if format_type == "joblib":
            model_file = model_dir / f"{model_name}{self.joblib_ext}"
            save_func = joblib.dump
        else:
            model_file = model_dir / f"{model_name}{self.pickle_ext}"
            save_func = lambda obj, path: pickle.dump(obj, open(path, 'wb'))
        
        try:
            # Save the model
            save_func(model, model_file)
            
            # Save metadata if provided
            if metadata:
                metadata_file = model_dir / f"{model_name}_metadata.json"
                import json
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
            
            # Create info file with model details
            info_file = model_dir / "model_info.txt"
            with open(info_file, 'w') as f:
                f.write(f"Model Information\n")
                f.write(f"================\n\n")
                f.write(f"Model Name: {model_name}\n")
                f.write(f"Model Type: {model_type}\n")
                f.write(f"Format: {format_type}\n")
                f.write(f"File: {model_file.name}\n")
                f.write(f"Saved: {Path().cwd()}\n")
                if hasattr(model, '__class__'):
                    f.write(f"Model Class: {model.__class__.__name__}\n")
                if metadata:
                    f.write(f"Metadata: {metadata_file.name}\n")
            
            print(f"Model saved successfully: {model_file}")
            return model_file
            
        except Exception as e:
            raise IOError(f"Failed to save model: {e}")
    
    def load_model(self, model_name: str, 
                   model_type: str = "general",
                   format_type: str = "auto") -> Tuple[Any, Optional[Dict]]:
        """
        Load a model with automatic format detection.
        
        Args:
            model_name (str): Name of the model to load
            model_type (str): Type/category of model
            format_type (str): Format to try ("joblib", "pickle", or "auto")
            
        Returns:
            Tuple[Any, Optional[Dict]]: (model_object, metadata)
            
        Raises:
            FileNotFoundError: If model file is not found
            IOError: If loading fails
        """
        model_dir = self.base_dir / model_type / model_name
        
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
        
        # Try to find model file
        model_file = None
        actual_format = None
        
        if format_type == "auto":
            # Try joblib first, then pickle
            formats_to_try = ["joblib", "pickle"] if JOBLIB_AVAILABLE else ["pickle"]
        else:
            formats_to_try = [format_type]
        
        for fmt in formats_to_try:
            if fmt == "joblib":
                candidate = model_dir / f"{model_name}{self.joblib_ext}"
                load_func = joblib.load if JOBLIB_AVAILABLE else None
            else:
                candidate = model_dir / f"{model_name}{self.pickle_ext}"
                load_func = lambda path: pickle.load(open(path, 'rb'))
            
            if candidate.exists() and load_func:
                model_file = candidate
                actual_format = fmt
                break
        
        if not model_file:
            available_files = list(model_dir.glob("*"))
            raise FileNotFoundError(
                f"Model file not found for {model_name} in {model_dir}. "
                f"Available files: {[f.name for f in available_files]}"
            )
        
        try:
            # Load the model
            if actual_format == "joblib":
                model = joblib.load(model_file)
            else:
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
            
            # Load metadata if available
            metadata = None
            metadata_file = model_dir / f"{model_name}_metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            print(f"Model loaded successfully: {model_file}")
            return model, metadata
            
        except Exception as e:
            raise IOError(f"Failed to load model: {e}")
    
    def list_models(self, model_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all available models.
        
        Args:
            model_type (Optional[str]): Filter by model type, or None for all
            
        Returns:
            Dict[str, List[str]]: Dictionary of model_type -> [model_names]
        """
        models = {}
        
        if model_type:
            search_dirs = [self.base_dir / model_type] if (self.base_dir / model_type).exists() else []
        else:
            search_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]
        
        for type_dir in search_dirs:
            type_name = type_dir.name
            model_names = []
            
            for model_dir in type_dir.iterdir():
                if model_dir.is_dir():
                    # Check if it contains model files
                    has_model = any(
                        (model_dir / f"{model_dir.name}{ext}").exists() 
                        for ext in [self.joblib_ext, self.pickle_ext]
                    )
                    if has_model:
                        model_names.append(model_dir.name)
            
            if model_names:
                models[type_name] = sorted(model_names)
        
        return models
    
    def get_model_info(self, model_name: str, model_type: str = "general") -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name (str): Name of the model
            model_type (str): Type/category of model
            
        Returns:
            Dict[str, Any]: Model information
            
        Raises:
            FileNotFoundError: If model is not found
        """
        model_dir = self.base_dir / model_type / model_name
        
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
        
        info = {
            'name': model_name,
            'type': model_type,
            'directory': str(model_dir),
            'files': []
        }
        
        # List all files in model directory
        for file_path in model_dir.iterdir():
            if file_path.is_file():
                info['files'].append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                })
        
        # Read info file if available
        info_file = model_dir / "model_info.txt"
        if info_file.exists():
            with open(info_file, 'r') as f:
                info['description'] = f.read()
        
        # Load metadata if available
        metadata_file = model_dir / f"{model_name}_metadata.json"
        if metadata_file.exists():
            import json
            with open(metadata_file, 'r') as f:
                info['metadata'] = json.load(f)
        
        return info
    
    def cleanup_old_models(self, model_type: str, keep_latest: int = 3) -> List[str]:
        """
        Clean up old model versions, keeping only the most recent ones.
        
        Args:
            model_type (str): Type of models to clean up
            keep_latest (int): Number of latest versions to keep
            
        Returns:
            List[str]: List of removed model names
        """
        type_dir = self.base_dir / model_type
        if not type_dir.exists():
            return []
        
        # Get all model directories with their modification times
        model_dirs = []
        for model_dir in type_dir.iterdir():
            if model_dir.is_dir():
                # Find the newest file in the directory
                newest_time = max(
                    (f.stat().st_mtime for f in model_dir.iterdir() if f.is_file()),
                    default=0
                )
                model_dirs.append((model_dir, newest_time))
        
        # Sort by modification time (newest first)
        model_dirs.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old models
        removed = []
        for model_dir, _ in model_dirs[keep_latest:]:
            try:
                import shutil
                shutil.rmtree(model_dir)
                removed.append(model_dir.name)
                print(f"Removed old model: {model_dir.name}")
            except Exception as e:
                print(f"Failed to remove {model_dir.name}: {e}")
        
        return removed


# Convenience functions for backward compatibility
def save_model(model: Any, filepath: Union[str, Path], 
               format_type: str = "auto", **kwargs) -> Path:
    """
    Convenience function to save a model using the default ModelManager.
    
    Args:
        model (Any): Model to save
        filepath (Union[str, Path]): Path where to save the model
        format_type (str): Format to use
        **kwargs: Additional arguments
        
    Returns:
        Path: Path to saved model
    """
    filepath = Path(filepath)
    model_name = filepath.stem
    model_type = kwargs.get('model_type', 'general')
    
    manager = ModelManager(filepath.parent)
    return manager.save_model(model, model_name, model_type, format_type)


def load_model(filepath: Union[str, Path], format_type: str = "auto") -> Any:
    """
    Convenience function to load a model using the default ModelManager.
    
    Args:
        filepath (Union[str, Path]): Path to the model file
        format_type (str): Format to try
        
    Returns:
        Any: Loaded model
    """
    filepath = Path(filepath)
    model_name = filepath.stem
    model_type = "general"
    
    manager = ModelManager(filepath.parent)
    model, _ = manager.load_model(model_name, model_type, format_type)
    return model


# Standard model locations for the project
PROJECT_MODEL_LOCATIONS = {
    'dcs_risk': {
        'directory': 'models/dcs',
        'files': ['trained_model.joblib', 'onehot_encoder.joblib', 'column_names.joblib'],
        'description': 'Decompression Sickness risk prediction models'
    },
    'tuc_prediction': {
        'directory': 'models/tuc',
        'files': ['tuc_model.joblib', 'tuc_altitude_model.joblib'],
        'description': 'Time of Useful Consciousness prediction models'
    },
    'fatigue_assessment': {
        'directory': 'models/fatigue',
        'files': ['fatigue_model.pkl'],
        'description': 'Fatigue and cognitive performance models'
    },
    'motion_sickness': {
        'directory': 'models/mssq',
        'files': ['mssq_model.pkl'],
        'description': 'Motion Sickness Susceptibility models'
    }
}


def get_project_model_info() -> Dict[str, Dict]:
    """
    Get information about standard model locations in the project.
    
    Returns:
        Dict[str, Dict]: Dictionary of model information
    """
    return PROJECT_MODEL_LOCATIONS.copy()


def validate_model_dependencies() -> Dict[str, bool]:
    """
    Validate that required libraries for model handling are available.
    
    Returns:
        Dict[str, bool]: Dictionary of library availability
    """
    dependencies = {
        'joblib': JOBLIB_AVAILABLE,
        'pickle': True,  # Always available in standard library
    }
    
    try:
        import json
        dependencies['json'] = True
    except ImportError:
        dependencies['json'] = False
    
    return dependencies


if __name__ == "__main__":
    # Example usage and testing
    print("Model Management Utilities")
    print("=" * 30)
    
    # Check dependencies
    deps = validate_model_dependencies()
    print("Dependencies:")
    for lib, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {lib}")
    
    print("\nProject Model Locations:")
    for model_type, info in get_project_model_info().items():
        print(f"  {model_type}: {info['directory']}")
        print(f"    Files: {', '.join(info['files'])}")
        print(f"    Description: {info['description']}")
        print() 