import numpy as np
import pandas as pd
from pathlib import Path
import pickle

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import Dense, Dropout
    from sklearn.preprocessing import StandardScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class RiskClassifier:
    """Machine Learning model to classify project risk levels"""

    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = None
        self.model_path = model_path or 'resources/models/risk_classifier.h5'
        self.scaler_path = 'resources/models/risk_scaler.pkl'
        self.risk_levels = ['Low', 'Medium', 'High', 'Critical']

        if not TENSORFLOW_AVAILABLE:
            print("Warning: TensorFlow not available. Risk classification will use fallback logic.")
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
            budget_variance_ratio = abs((project['BUDGET'] - project['ACTUAL_COST']) / project['BUDGET'])
        else:
            budget_variance_ratio = 0
        features.append(budget_variance_ratio)

        # CCR completion ratio
        if metrics.get('total_ccrs', 0) > 0:
            ccr_completion_ratio = metrics.get('completed_ccrs', 0) / metrics['total_ccrs']
        else:
            ccr_completion_ratio = 1.0
        features.append(ccr_completion_ratio)

        # Order completion ratio
        if metrics.get('total_orders', 0) > 0:
            order_completion_ratio = metrics.get('completed_orders', 0) / metrics['total_orders']
        else:
            order_completion_ratio = 1.0
        features.append(order_completion_ratio)

        # Hours variance ratio
        if metrics.get('estimated_hours', 0) > 0:
            hours_variance_ratio = abs((metrics.get('actual_hours', 0) - metrics['estimated_hours']) / metrics['estimated_hours'])
        else:
            hours_variance_ratio = 0
        features.append(hours_variance_ratio)

        # Total CCRs (complexity indicator)
        features.append(metrics.get('total_ccrs', 0))

        # Total orders (complexity indicator)
        features.append(metrics.get('total_orders', 0))

        # Budget amount (normalized)
        features.append(project.get('BUDGET', 0) / 1000000)  # Normalize to millions

        # Project age (if ongoing)
        if project.get('START_DATE'):
            from datetime import datetime
            age_days = (datetime.now() - project['START_DATE']).days
            features.append(age_days)
        else:
            features.append(0)

        return np.array(features).reshape(1, -1)

    def classify(self, project: dict, metrics: dict) -> dict:
        """Classify risk level for a project"""
        features = self._extract_features(project, metrics)

        if self.model is None or self.scaler is None:
            # Fallback classification based on simple heuristics
            return self._fallback_classification(project, metrics, features)

        try:
            # Scale features
            features_scaled = self.scaler.transform(features)

            # Make prediction
            predictions = self.model.predict(features_scaled, verbose=0)[0]
            risk_index = np.argmax(predictions)
            risk_level = self.risk_levels[risk_index]
            confidence = float(predictions[risk_index])

            return {
                'risk_level': risk_level,
                'confidence': confidence,
                'factors': {
                    'budget_variance': float(features[0][0]),
                    'ccr_completion': float(features[0][1]),
                    'order_completion': float(features[0][2]),
                    'hours_variance': float(features[0][3]),
                    'complexity': int(features[0][4] + features[0][5])
                }
            }
        except Exception as e:
            print(f"Classification error: {e}")
            return self._fallback_classification(project, metrics, features)

    def _fallback_classification(self, project: dict, metrics: dict, features: np.array) -> dict:
        """Simple heuristic-based classification when ML model is unavailable"""
        risk_score = 0

        # Budget variance (0-25 points)
        budget_var = features[0][0]
        if budget_var > 0.3:
            risk_score += 25
        elif budget_var > 0.2:
            risk_score += 20
        elif budget_var > 0.1:
            risk_score += 10

        # CCR completion (0-25 points)
        ccr_completion = features[0][1]
        if ccr_completion < 0.5:
            risk_score += 25
        elif ccr_completion < 0.7:
            risk_score += 15
        elif ccr_completion < 0.9:
            risk_score += 5

        # Order completion (0-25 points)
        order_completion = features[0][2]
        if order_completion < 0.5:
            risk_score += 25
        elif order_completion < 0.7:
            risk_score += 15
        elif order_completion < 0.9:
            risk_score += 5

        # Hours variance (0-25 points)
        hours_var = features[0][3]
        if hours_var > 0.3:
            risk_score += 25
        elif hours_var > 0.2:
            risk_score += 15
        elif hours_var > 0.1:
            risk_score += 5

        # Determine risk level based on score
        if risk_score < 25:
            risk_level = 'Low'
            confidence = 0.65
        elif risk_score < 50:
            risk_level = 'Medium'
            confidence = 0.60
        elif risk_score < 75:
            risk_level = 'High'
            confidence = 0.55
        else:
            risk_level = 'Critical'
            confidence = 0.50

        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'factors': {
                'budget_variance': float(features[0][0]),
                'ccr_completion': float(features[0][1]),
                'order_completion': float(features[0][2]),
                'hours_variance': float(features[0][3]),
                'complexity': int(features[0][4] + features[0][5])
            }
        }

    def train(self, projects: list) -> dict:
        """Train the risk classification model"""
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

            # Determine risk label based on project status
            # This is simplified; actual labels would come from historical data
            if project.get('PROJECT_STATUS') == 'COMPLETED':
                label = 0  # Low risk (completed successfully)
            elif project.get('PROJECT_STATUS') == 'ON_HOLD':
                label = 3  # Critical risk
            else:
                label = 1  # Medium risk (default)

            # One-hot encode label
            one_hot = [0] * len(self.risk_levels)
            one_hot[label] = 1
            y.append(one_hot)

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
            Dense(len(self.risk_levels), activation='softmax')  # Output: risk probabilities
        ])

        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
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
                ('risk_classifier', history.history['accuracy'][-1], len(X), self.model_path)
            )

        return {
            'samples': len(X),
            'final_loss': float(history.history['loss'][-1]),
            'final_accuracy': float(history.history['accuracy'][-1])
        }
