from fastapi import APIRouter, HTTPException
from models import MLPrediction
from core.oracle_manager import OracleManager
import numpy as np
from pathlib import Path

router = APIRouter()

@router.get("/predict-delay/{project_number}", response_model=MLPrediction)
async def predict_delay(project_number: str):
    """Predict project delay using ML model"""
    try:
        from ml.delay_predictor import DelayPredictor

        with OracleManager() as db:
            project = db.get_project_by_number(project_number)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            metrics = db.get_project_metrics(project_number)

        # Initialize and use predictor
        predictor = DelayPredictor()
        prediction = predictor.predict(project, metrics)

        return {
            'project_number': project_number,
            'predicted_delay_days': prediction['delay_days'],
            'risk_level': prediction['risk_level'],
            'confidence': prediction['confidence'],
            'factors': prediction['factors']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classify-risk/{project_number}", response_model=MLPrediction)
async def classify_risk(project_number: str):
    """Classify project risk level using ML model"""
    try:
        from ml.risk_classifier import RiskClassifier

        with OracleManager() as db:
            project = db.get_project_by_number(project_number)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            metrics = db.get_project_metrics(project_number)

        # Initialize and use classifier
        classifier = RiskClassifier()
        prediction = classifier.classify(project, metrics)

        return {
            'project_number': project_number,
            'risk_level': prediction['risk_level'],
            'confidence': prediction['confidence'],
            'factors': prediction['factors']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
async def retrain_models():
    """Retrain ML models with latest data"""
    try:
        from ml.delay_predictor import DelayPredictor
        from ml.risk_classifier import RiskClassifier

        with OracleManager() as db:
            # Get all completed projects for training
            projects = db.get_projects({'status': 'COMPLETED'})

            if len(projects) < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient data for training (minimum 100 completed projects required)"
                )

        # Train delay predictor
        delay_predictor = DelayPredictor()
        delay_metrics = delay_predictor.train(projects)

        # Train risk classifier
        risk_classifier = RiskClassifier()
        risk_metrics = risk_classifier.train(projects)

        return {
            'message': 'Models retrained successfully',
            'delay_predictor': delay_metrics,
            'risk_classifier': risk_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """Get information about ML models"""
    try:
        from core.sqlite_manager import SQLiteManager

        with SQLiteManager() as db:
            history = db.execute_query(
                "SELECT * FROM ml_training_history ORDER BY training_date DESC LIMIT 10"
            )

        return {
            'training_history': history,
            'models': {
                'delay_predictor': {
                    'type': 'Neural Network',
                    'architecture': 'Sequential (Dense layers)',
                    'features': ['budget_variance', 'completion_ratio', 'estimated_hours', 'actual_hours']
                },
                'risk_classifier': {
                    'type': 'Neural Network',
                    'architecture': 'Sequential (Dense layers)',
                    'classes': ['Low', 'Medium', 'High', 'Critical']
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
