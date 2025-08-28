from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

# Usando importações absolutas a partir da raiz do projeto (backend)
from backend.ml.churn_predictor import ChurnMLService
from backend.core.database import get_db

router = APIRouter()


@router.post("/train_churn_model", tags=["Machine Learning"])
def train_churn_model(db: Session = Depends(get_db)):
    """
    Endpoint para treinar o modelo de previsão de churn.
    """
    try:
        ml_service = ChurnMLService(db=db)
        result = ml_service.train_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict_churn", tags=["Machine Learning"])
def predict_churn(input_data: dict, db: Session = Depends(get_db)):
    """
    Endpoint para fazer previsões de churn.
    O input_data deve ser um dicionário que pode ser convertido em um DataFrame do Pandas.
    Exemplo: {'feature1': [0.5], 'feature2': [1.2], ...}
    """
    try:
        df = pd.DataFrame(input_data)
        ml_service = ChurnMLService(db=db)
        predictions = ml_service.predict(df)
        return {"predictions": predictions.tolist()}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
