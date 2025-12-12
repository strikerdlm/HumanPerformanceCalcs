"""Model persistence helpers.

Security note
- Pickle is unsafe for untrusted inputs. This module therefore **requires an
  explicit opt-in** (``allow_pickle=True``) to save or load pickle models.

Design goals
- Import-safe (no warnings/prints at import time)
- Deterministic, bounded loops
- Explicit input validation and clear error messages
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Mapping

try:
    import joblib  # type: ignore

    _JOBLIB_AVAILABLE = True
except Exception:  # pragma: no cover
    joblib = None  # type: ignore
    _JOBLIB_AVAILABLE = False

import json
import pickle


class ModelManager:
    """Centralized model save/load with consistent on-disk layout."""

    def __init__(self, base_dir: str | Path = "models") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.joblib_ext = ".joblib"
        self.pickle_ext = ".pkl"

    def save_model(
        self,
        model: Any,
        model_name: str,
        model_type: str = "general",
        format_type: str = "auto",
        metadata: Optional[Mapping[str, Any]] = None,
        *,
        allow_pickle: bool = False,
    ) -> Path:
        """Save a model to disk.

        Layout
            {base_dir}/{model_type}/{model_name}/{model_name}.{ext}

        Args:
            model: Arbitrary Python object.
            model_name: Logical name (used for directory + filename stem).
            model_type: Category grouping.
            format_type: 'auto' | 'joblib' | 'pickle'.
            metadata: Optional JSON-serializable metadata mapping.
            allow_pickle: Required to use pickle.

        Returns:
            Path to saved model file.

        Raises:
            ValueError: For unsupported format or unsafe pickle usage.
            OSError: For file system failures.
        """

        name = str(model_name).strip()
        mtype = str(model_type).strip() or "general"
        fmt = str(format_type).strip().lower()

        if not name:
            raise ValueError("model_name must be non-empty")

        if fmt == "auto":
            fmt = "joblib" if _JOBLIB_AVAILABLE else "pickle"

        if fmt not in {"joblib", "pickle"}:
            raise ValueError("format_type must be 'auto', 'joblib', or 'pickle'")

        if fmt == "pickle" and not allow_pickle:
            raise ValueError(
                "Refusing to save with pickle unless allow_pickle=True (pickle is unsafe for untrusted inputs)."
            )

        if fmt == "joblib" and not _JOBLIB_AVAILABLE:
            raise ValueError("joblib is not available; install it or use pickle with allow_pickle=True")

        model_dir = self.base_dir / mtype / name
        model_dir.mkdir(parents=True, exist_ok=True)

        if fmt == "joblib":
            model_file = model_dir / f"{name}{self.joblib_ext}"
            assert joblib is not None
            joblib.dump(model, model_file)
        else:
            model_file = model_dir / f"{name}{self.pickle_ext}"
            with model_file.open("wb") as f:
                pickle.dump(model, f)

        if metadata is not None:
            metadata_file = model_dir / f"{name}_metadata.json"
            with metadata_file.open("w", encoding="utf-8") as f:
                json.dump(dict(metadata), f, indent=2, default=str)

        info_file = model_dir / "model_info.json"
        info_payload: dict[str, Any] = {
            "model_name": name,
            "model_type": mtype,
            "format": fmt,
            "file": model_file.name,
        }
        with info_file.open("w", encoding="utf-8") as f:
            json.dump(info_payload, f, indent=2)

        return model_file

    def load_model(
        self,
        model_name: str,
        model_type: str = "general",
        format_type: str = "auto",
        *,
        allow_pickle: bool = False,
    ) -> tuple[Any, Optional[dict[str, Any]]]:
        """Load a model from disk.

        Args:
            model_name: Logical name.
            model_type: Category grouping.
            format_type: 'auto' | 'joblib' | 'pickle'.
            allow_pickle: Required to load pickles.

        Returns:
            (model_object, metadata_dict_or_none)

        Raises:
            FileNotFoundError: If the model directory/file is missing.
            ValueError: For unsupported format or unsafe pickle usage.
            OSError: For load/deserialize failures.
        """

        name = str(model_name).strip()
        mtype = str(model_type).strip() or "general"
        fmt = str(format_type).strip().lower()

        if not name:
            raise ValueError("model_name must be non-empty")

        model_dir = self.base_dir / mtype / name
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        formats_to_try: list[str]
        if fmt == "auto":
            formats_to_try = ["joblib", "pickle"]
        elif fmt in {"joblib", "pickle"}:
            formats_to_try = [fmt]
        else:
            raise ValueError("format_type must be 'auto', 'joblib', or 'pickle'")

        model_file: Optional[Path] = None
        chosen_fmt: Optional[str] = None

        for candidate_fmt in formats_to_try:
            if candidate_fmt == "joblib":
                candidate = model_dir / f"{name}{self.joblib_ext}"
                if candidate.exists():
                    if not _JOBLIB_AVAILABLE:
                        continue
                    model_file = candidate
                    chosen_fmt = "joblib"
                    break
            else:
                candidate = model_dir / f"{name}{self.pickle_ext}"
                if candidate.exists():
                    model_file = candidate
                    chosen_fmt = "pickle"
                    break

        if model_file is None or chosen_fmt is None:
            available = sorted(p.name for p in model_dir.glob("*") if p.is_file())
            raise FileNotFoundError(
                f"Model file not found for '{name}' in {model_dir}. Available files: {available}"
            )

        if chosen_fmt == "pickle" and not allow_pickle:
            raise ValueError(
                "Refusing to load pickle unless allow_pickle=True (pickle is unsafe for untrusted inputs)."
            )

        if chosen_fmt == "joblib":
            assert joblib is not None
            model = joblib.load(model_file)
        else:
            with model_file.open("rb") as f:
                model = pickle.load(f)

        metadata: Optional[dict[str, Any]] = None
        metadata_file = model_dir / f"{name}_metadata.json"
        if metadata_file.exists():
            with metadata_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                metadata = loaded

        return model, metadata

    def list_models(self, model_type: Optional[str] = None) -> dict[str, list[str]]:
        """List available models under base_dir."""

        result: dict[str, list[str]] = {}

        search_dirs: list[Path]
        if model_type is not None:
            tdir = self.base_dir / str(model_type)
            search_dirs = [tdir] if tdir.exists() else []
        else:
            search_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]

        for type_dir in search_dirs:
            model_names: list[str] = []
            for model_dir in type_dir.iterdir():
                if not model_dir.is_dir():
                    continue
                stem = model_dir.name
                has_joblib = (model_dir / f"{stem}{self.joblib_ext}").exists()
                has_pickle = (model_dir / f"{stem}{self.pickle_ext}").exists()
                if has_joblib or has_pickle:
                    model_names.append(stem)
            if model_names:
                result[type_dir.name] = sorted(model_names)

        return result

    def get_model_info(self, model_name: str, model_type: str = "general") -> dict[str, Any]:
        """Return metadata and file inventory for a stored model."""

        name = str(model_name).strip()
        mtype = str(model_type).strip() or "general"
        if not name:
            raise ValueError("model_name must be non-empty")

        model_dir = self.base_dir / mtype / name
        if not model_dir.exists():
            raise FileNotFoundError(f"Model directory not found: {model_dir}")

        files = sorted(
            {
                "name": p.name,
                "size": p.stat().st_size,
                "modified": p.stat().st_mtime,
            }
            for p in model_dir.iterdir()
            if p.is_file()
        )

        info: dict[str, Any] = {
            "name": name,
            "type": mtype,
            "directory": str(model_dir),
            "files": files,
        }

        info_file = model_dir / "model_info.json"
        if info_file.exists():
            with info_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                info["info"] = loaded

        metadata_file = model_dir / f"{name}_metadata.json"
        if metadata_file.exists():
            with metadata_file.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                info["metadata"] = loaded

        return info

    def cleanup_old_models(
        self,
        model_type: str,
        *,
        keep_latest: int = 3,
        allow_delete: bool = False,
    ) -> list[str]:
        """Plan (or perform) cleanup of old model directories.

        By default this function **does not delete anything** (allow_delete=False)
        to avoid accidental data loss.

        Args:
            model_type: Directory under base_dir.
            keep_latest: Number of newest model dirs to keep.
            allow_delete: When True, will delete old directories.

        Returns:
            List of model directory names that were deleted (or would be deleted).
        """

        if keep_latest < 0:
            raise ValueError("keep_latest must be >= 0")

        type_dir = self.base_dir / str(model_type)
        if not type_dir.exists():
            return []

        model_dirs: list[tuple[Path, float]] = []
        for model_dir in type_dir.iterdir():
            if not model_dir.is_dir():
                continue
            newest_time = 0.0
            for p in model_dir.iterdir():
                if p.is_file():
                    newest_time = max(newest_time, float(p.stat().st_mtime))
            model_dirs.append((model_dir, newest_time))

        model_dirs.sort(key=lambda x: x[1], reverse=True)
        targets = [d.name for d, _ in model_dirs[keep_latest:]]

        if not allow_delete:
            return targets

        # Deletion is explicitly opt-in.
        import shutil

        deleted: list[str] = []
        for d, _ in model_dirs[keep_latest:]:
            shutil.rmtree(d)
            deleted.append(d.name)

        return deleted


# Convenience functions for backward compatibility

def save_model(
    model: Any,
    filepath: str | Path,
    format_type: str = "auto",
    **kwargs: Any,
) -> Path:
    """Save a model to a filepath-like location.

    Note: To use pickle, pass allow_pickle=True.
    """

    path = Path(filepath)
    manager = ModelManager(path.parent)
    return manager.save_model(
        model,
        model_name=path.stem,
        model_type=str(kwargs.get("model_type", "general")),
        format_type=format_type,
        metadata=kwargs.get("metadata"),
        allow_pickle=bool(kwargs.get("allow_pickle", False)),
    )


def load_model(filepath: str | Path, format_type: str = "auto", *, allow_pickle: bool = False) -> Any:
    """Load a model from a filepath-like location.

    Security: pickle requires allow_pickle=True.
    """

    path = Path(filepath)
    manager = ModelManager(path.parent)
    model, _ = manager.load_model(path.stem, model_type="general", format_type=format_type, allow_pickle=allow_pickle)
    return model


PROJECT_MODEL_LOCATIONS: dict[str, dict[str, Any]] = {
    "dcs_risk": {
        "directory": "models/dcs",
        "files": ["trained_model.joblib", "onehot_encoder.joblib", "column_names.joblib"],
        "description": "Decompression Sickness risk prediction models",
    },
    "tuc_prediction": {
        "directory": "models/tuc",
        "files": ["tuc_model.joblib", "tuc_altitude_model.joblib"],
        "description": "Time of Useful Consciousness prediction models",
    },
    "fatigue_assessment": {
        "directory": "models/fatigue",
        "files": ["fatigue_model.pkl"],
        "description": "Fatigue and cognitive performance models",
    },
    "motion_sickness": {
        "directory": "models/mssq",
        "files": ["mssq_model.pkl"],
        "description": "Motion Sickness Susceptibility models",
    },
}


def get_project_model_info() -> dict[str, dict[str, Any]]:
    """Return the standard model layout map."""

    return dict(PROJECT_MODEL_LOCATIONS)


def validate_model_dependencies() -> dict[str, bool]:
    """Report availability of model persistence backends."""

    return {
        "joblib": _JOBLIB_AVAILABLE,
        "pickle": True,
        "json": True,
    }
