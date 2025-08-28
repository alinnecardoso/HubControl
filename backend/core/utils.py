import joblib
from typing import Any

def save_model(model: Any, filepath: str) -> None:
    """Saves the model to a file."""
    joblib.dump(model, filepath)

def load_model(filepath: str) -> Any:
    """Loads the model from a file."""
    return joblib.load(filepath)
