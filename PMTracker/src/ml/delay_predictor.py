import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import pickle

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, Dropout
    from sklearn.preprocessing import StandardScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class DelayPredictor:
    """Machine Learning model to predict project delays"""

    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = None
        self.model_path = model_path or 'resources/models/delay_predictor.h5'
        self.scaler_path = 'resources/models/delay_scaler.pkl'

        if not TENSORFLOW_AVAILABLE:
            print("Warning: TensorFlow not available. ML predictions will use fallback logic.")
            return

        # Load existing model if available
        model_file = Path(self.model_path)
        scaler_file = Path(self.scaler_path)

        if model_file.exists() and scaler_file.exists():
            try:
                self.model = load_model(str(model_file))
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
            except Exception as e:
                print(f"Error loading model: {e}")

    def _extract_features(self, project: dict, metrics: dict) -> np.array:
        """Extract features from project data"""
        features = []

        # Budget variance ratio
        if project.get('BUDGET') and project.get('ACTUAL_COST'):
            budget_variance_ratio = (project['BUDGET'] - project['ACTUAL_COST']) / project['BUDGET']
        else:
            budget_variance_ratio = 0
        features.append(budget_variance_ratio)

        # CCR completion ratio
        if metrics.get('total_ccrs', 0) > 0:
            ccr_completion_ratio = metrics.get('completed_ccrs', 0) / metrics['total_ccrs']
        else:
            ccr_completion_ratio = 0
        features.append(ccr_completion_ratio)

        # Order completion ratio
        if metrics.get('total_orders', 0) > 0:
            order_completion_ratio = metrics.get('completed_orders', 0) / metrics['total_orders']
        else:
            order_completion_ratio = 0
        features.append(order_completion_ratio)

        # Hours variance ratio
        if metrics.get('estimated_hours', 0) > 0:
            hours_variance_ratio = (metrics.get('actual_hours', 0) - metrics['estimated_hours']) / metrics['estimated_hours']
        else:
            hours_variance_ratio = 0
        features.append(hours_variance_ratio)

        # Project duration (days)
        if project.get('START_DATE') and project.get('END_DATE'):
            duration = (project['END_DATE'] - project['START_DATE']).days
        else:
            duration = 0
        features.append(duration)

        # Total CCRs
        features.append(metrics.get('total_ccrs', 0))

        # Total orders
        features.append(metrics.get('total_orders', 0))

        # Budget amount (normalized)
        features.append(project.get('BUDGET', 0) / 1000000)  # Normalize to millions

        return np.array(features).reshape(1, -1)

    def predict(self, project: dict, metrics: dict) -> dict:
        """Predict delay for a project"""
        features = self._extract_features(project, metrics)

        if self.model is None or self.scaler is None:
            # Fallback prediction based on simple heuristics
            return self._fallback_prediction(project, metrics, features)

        try:
            # Scale features
            features_scaled = self.scaler.transform(features)

            # Make prediction
            delay_days = self.model.predict(features_scaled, verbose=0)[0][0]

            # Determine risk level
            if delay_days < 0:
                risk_level = 'Low'
                confidence = 0.85
            elif delay_days < 30:
                risk_level = 'Medium'
                confidence = 0.80
            elif delay_days < 60:
                risk_level = 'High'
                confidence = 0.75
            else:
                risk_level = 'Critical'
                confidence = 0.70

            return {
                'delay_days': int(delay_days),
                'risk_level': risk_level,
                'confidence': confidence,
                'factors': {
                    'budget_variance': features[0][0],
                    'ccr_completion': features[0][1],
                    'order_completion': features[0][2],
                    'hours_variance': features[0][3]
                }
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._fallback_prediction(project, metrics, features)

    def _fallback_prediction(self, project: dict, metrics: dict, features: np.array) -> dict:
        """Simple heuristic-based prediction when ML model is unavailable"""
        # Calculate delay based on simple rules
        delay_score = 0

        # Budget overrun
        if features[0][0] < -0.1:  # 10% over budget
            delay_score += 20

        # Low CCR completion
        if features[0][1] < 0.5:
            delay_score += 15

        # Low order completion
        if features[0][2] < 0.5:
            delay_score += 15

        # Hours overrun
        if features[0][3] > 0.2:  # 20% more hours
            delay_score += 20

        # Determine risk level
        if delay_score < 20:
            risk_level = 'Low'
            confidence = 0.60
        elif delay_score < 40:
            risk_level = 'Medium'
            confidence = 0.55
        elif delay_score < 60:
            risk_level = 'High'
            confidence = 0.50
        else:
            risk_level = 'Critical'
            confidence = 0.45

        return {
            'delay_days': delay_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'factors': {
                'budget_variance': float(features[0][0]),
                'ccr_completion': float(features[0][1]),
                'order_completion': float(features[0][2]),
                'hours_variance': float(features[0][3])
            }
        }

    def train(self, projects: list) -> dict:
        """Train the delay prediction model"""
        if not TENSORFLOW_AVAILABLE:
            return {'error': 'TensorFlow not available for training'}

        # Prepare training data
        X = []
        y = []

        for project in projects:
            from core.oracle_manager import OracleManager
            with OracleManager() as db:
                metrics = db.get_project_metrics(project['PROJECT_NUMBER'])

            features = self._extract_features(project, metrics)
            X.append(features[0])

            # Calculate actual delay (label)
            if project.get('START_DATE') and project.get('END_DATE'):
                planned_duration = (project['END_DATE'] - project['START_DATE']).days
                # This is simplified; actual delay would need completion date
                actual_delay = 0  # Placeholder
                y.append(actual_delay)

        X = np.array(X)
        y = np.array(y)

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Build model
        self.model = Sequential([
            Dense(64, activation='relu', input_shape=(X.shape[1],)),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Output: delay in days
        ])

        self.model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']
        )

        # Train model
        history = self.model.fit(
            X_scaled, y,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )

        # Save model
        model_dir = Path(self.model_path).parent
        model_dir.mkdir(parents=True, exist_ok=True)

        self.model.save(str(self.model_path))
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        # Save training history to database
        from core.sqlite_manager import SQLiteManager
        with SQLiteManager() as db:
            db.execute_update(
                "INSERT INTO ml_training_history (model_type, accuracy, training_samples, model_path) VALUES (?, ?, ?, ?)",
                ('delay_predictor', history.history['mae'][-1], len(X), self.model_path)
            )

        return {
            'samples': len(X),
            'final_loss': float(history.history['loss'][-1]),
            'final_mae': float(history.history['mae'][-1])
        }
