"""
TensorFlow-based machine learning model for personalized learning recommendations.

Implements:
- Neural network for user/topic interaction prediction
- Data preprocessing pipeline
- Model training and evaluation
- Model persistence and loading
- Inference service for recommendations
"""

import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

# Check if we should skip ML engine (e.g. for testing or if TF is broken)
SKIP_ML = os.getenv("SKIP_ML_ENGINE", "false").lower() == "true"

try:
    if SKIP_ML:
        raise ImportError("ML Engine skipped via environment variable")
        
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Sequential
    TF_AVAILABLE = True
except ImportError:
    tf = None
    keras = None
    layers = None
    Sequential = None
    TF_AVAILABLE = False
    if not SKIP_ML:
        logger.warning("TensorFlow not available. ML features will be disabled.")
except Exception as e:
    # Catch other errors like protobuf version mismatch
    tf = None
    keras = None
    layers = None
    Sequential = None
    TF_AVAILABLE = False
    logger.warning(f"Error importing TensorFlow: {e}. ML features will be disabled.")
import json
import pickle
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from datetime import datetime


class UserProfileEncoder:
    """Encodes user profiles and interactions into feature vectors."""
    
    def __init__(self, max_users: int = 10000, max_topics: int = 1000):
        self.max_users = max_users
        self.max_topics = max_topics
        self.user_mapping = {}
        self.topic_mapping = {}
        self.reverse_user_map = {}
        self.reverse_topic_map = {}
        self.interaction_stats = {}
    
    def add_user(self, user_id: str) -> int:
        """Map user_id to integer index."""
        if user_id not in self.user_mapping:
            idx = len(self.user_mapping)
            if idx >= self.max_users:
                raise ValueError(f"Max users ({self.max_users}) exceeded")
            self.user_mapping[user_id] = idx
            self.reverse_user_map[idx] = user_id
        return self.user_mapping[user_id]
    
    def add_topic(self, topic_id: int) -> int:
        """Map topic_id to integer index."""
        if topic_id not in self.topic_mapping:
            idx = len(self.topic_mapping)
            if idx >= self.max_topics:
                raise ValueError(f"Max topics ({self.max_topics}) exceeded")
            self.topic_mapping[topic_id] = idx
            self.reverse_topic_map[idx] = topic_id
        return self.topic_mapping[topic_id]
    
    def encode_interaction(self, user_id: str, topic_id: int, completion: float, 
                          quiz_score: float, time_spent: int) -> Dict:
        """Encode user interaction into feature vector."""
        user_idx = self.add_user(user_id)
        topic_idx = self.add_topic(topic_id)
        
        # Normalize features to 0-1 range
        completion_norm = min(completion / 100.0, 1.0)
        quiz_norm = min(quiz_score / 100.0, 1.0)
        time_norm = min(time_spent / 7200.0, 1.0)  # Normalize to 2 hours max
        
        # Calculate engagement score
        engagement = (completion_norm + quiz_norm + time_norm) / 3.0
        
        return {
            "user_idx": user_idx,
            "topic_idx": topic_idx,
            "completion": completion_norm,
            "quiz_score": quiz_norm,
            "time_spent": time_norm,
            "engagement": engagement
        }
    
    def save(self, filepath: str):
        """Persist encoder mappings."""
        data = {
            "user_mapping": self.user_mapping,
            "topic_mapping": self.topic_mapping,
            "reverse_user_map": {str(k): v for k, v in self.reverse_user_map.items()},
            "reverse_topic_map": {str(k): v for k, v in self.reverse_topic_map.items()}
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, filepath: str):
        """Load encoder mappings."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.user_mapping = data["user_mapping"]
        self.topic_mapping = data["topic_mapping"]
        self.reverse_user_map = {int(k): v for k, v in data["reverse_user_map"].items()}
        self.reverse_topic_map = {int(k): v for k, v in data["reverse_topic_map"].items()}


class RecommendationModel:
    """Neural network model for learning recommendations."""
    
    def __init__(self, embedding_dim: int = 64, dense_units: int = 128):
        """
        Initialize model architecture.
        
        Args:
            embedding_dim: Dimension of user/topic embeddings
            dense_units: Units in dense layers
        """
        self.embedding_dim = embedding_dim
        self.dense_units = dense_units
        self.model = None
        self.encoder = UserProfileEncoder()
        self.created_at = datetime.utcnow()
        self.trained = False
        
    def build(self, num_users: int, num_topics: int):
        """Build the neural network architecture."""
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available, cannot build model")
            return

        self.model = Sequential([
            # Input layer with feature engineering
            layers.Input(shape=(7,)),  # user_idx, topic_idx, completion, quiz, time, engagement, bonus_features
            
            # Feature processing
            layers.Dense(256, activation='relu', name='feature_processing'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Mid-level processing
            layers.Dense(128, activation='relu', name='mid_processing'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Feature extraction
            layers.Dense(64, activation='relu', name='feature_extraction'),
            layers.Dropout(0.2),
            
            # Output prediction (0-1 probability of good match)
            layers.Dense(1, activation='sigmoid', name='output')
        ])
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC()]
        )
        
        logger.info(f"Model built with {self.model.count_params()} parameters")
    
    def prepare_training_data(self, interactions: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from user interactions.
        
        Args:
            interactions: List of interaction records
            
        Returns:
            X (features), y (labels - whether interaction was successful)
        """
        X = []
        y = []
        
        for interaction in interactions:
            # Extract features
            features = [
                self.encoder.add_user(interaction['user_id']),
                self.encoder.add_topic(interaction['topic_id']),
                min(interaction.get('completion_percentage', 0) / 100.0, 1.0),
                min(interaction.get('quiz_score', 0) / 100.0, 1.0),
                min(interaction.get('time_spent_seconds', 0) / 3600.0, 1.0),  # Normalize to hours
                interaction.get('engagement_score', 0.5),
                interaction.get('difficulty_adjustment', 0.5)
            ]
            X.append(features)
            
            # Label: successful if completion > 60% and quiz score > 70%
            success = 1 if (
                interaction.get('completion_percentage', 0) > 60 and 
                interaction.get('quiz_score', 0) > 70
            ) else 0
            y.append(success)
        
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
    
    def train(self, interactions: List[Dict], epochs: int = 50, validation_split: float = 0.2):
        """
        Train the model on interaction data.
        
        Args:
            interactions: User interaction records
            epochs: Number of training epochs
            validation_split: Fraction of data to use for validation
        """
        if not self.model:
            raise ValueError("Model must be built before training")
        
        X, y = self.prepare_training_data(interactions)
        
        if len(X) == 0:
            logger.warning("No training data available")
            return
        
        # Early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=32,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=1
        )
        
        self.trained = True
        logger.info("Model training completed")
        
        return history
    
    def evaluate(self, test_interactions: List[Dict]) -> Dict:
        """Evaluate model on test data."""
        X, y = self.prepare_training_data(test_interactions)
        
        if len(X) == 0:
            return {"error": "No test data"}
        
        loss, accuracy, auc = self.model.evaluate(X, y, verbose=0)
        
        return {
            "loss": float(loss),
            "accuracy": float(accuracy),
            "auc": float(auc)
        }
    
    def predict_recommendation_score(self, user_id: str, topic_id: int, 
                                    current_progress: Dict) -> float:
        """
        Predict recommendation score for user/topic pair.
        
        Args:
            user_id: User identifier
            topic_id: Topic identifier
            current_progress: User's current progress data
            
        Returns:
            Score between 0-1 indicating recommendation strength
        """
        if not self.trained:
            logger.warning("Model not trained, using default score")
            return 0.5
        
        features = np.array([[
            self.encoder.add_user(user_id),
            self.encoder.add_topic(topic_id),
            min(current_progress.get('completion_percentage', 0) / 100.0, 1.0),
            min(current_progress.get('quiz_score', 0) / 100.0, 1.0),
            min(current_progress.get('time_spent_seconds', 0) / 3600.0, 1.0),
            current_progress.get('engagement_score', 0.5),
            0.5  # Neutral difficulty adjustment for new prediction
        ]], dtype=np.float32)
        
        score = float(self.model.predict(features, verbose=0)[0][0])
        return score
    
    def save(self, model_dir: str):
        """Save model and encoder."""
        path = Path(model_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save model weights
        self.model.save(str(path / "model.keras"))
        
        # Save encoder
        self.encoder.save(str(path / "encoder.json"))
        
        # Save metadata
        metadata = {
            "embedding_dim": self.embedding_dim,
            "dense_units": self.dense_units,
            "created_at": self.created_at.isoformat(),
            "trained": self.trained
        }
        with open(path / "metadata.json", 'w') as f:
            json.dump(metadata, f)
        
        logger.info(f"Model saved to {model_dir}")
    
    def load(self, model_dir: str):
        """Load model and encoder."""
        path = Path(model_dir)
        
        # Load model
        if TF_AVAILABLE:
            self.model = keras.models.load_model(str(path / "model.keras"))
        else:
            logger.warning("TensorFlow not available, cannot load model")
        
        # Load encoder
        self.encoder.load(str(path / "encoder.json"))
        
        # Load metadata
        with open(path / "metadata.json", 'r') as f:
            metadata = json.load(f)
        
        self.embedding_dim = metadata["embedding_dim"]
        self.dense_units = metadata["dense_units"]
        self.trained = metadata["trained"]
        
        logger.info(f"Model loaded from {model_dir}")


class RecommendationEngine:
    """High-level interface for generating recommendations."""
    
    def __init__(self, model_dir: Optional[str] = None):
        """Initialize recommendation engine."""
        self.model = RecommendationModel()
        
        if model_dir and Path(model_dir).exists():
            self.model.load(model_dir)
        else:
            # Build and initialize
            self.model.build(num_users=10000, num_topics=1000)
    
    def get_recommendations(self, user_id: str, available_topics: List[int],
                           user_progress: Dict) -> List[Dict]:
        """
        Get top recommended topics for a user.
        
        Args:
            user_id: User identifier
            available_topics: List of topic IDs to consider
            user_progress: User's progress across topics
            
        Returns:
            Sorted list of topic recommendations with scores
        """
        recommendations = []
        
        for topic_id in available_topics:
            topic_progress = user_progress.get(topic_id, {
                "completion_percentage": 0,
                "quiz_score": 0,
                "time_spent_seconds": 0,
                "engagement_score": 0.5
            })
            
            # Skip if user completed the topic
            if topic_progress.get("completion_percentage", 0) >= 95:
                continue
            
            score = self.model.predict_recommendation_score(
                user_id, topic_id, topic_progress
            )
            
            recommendations.append({
                "topic_id": topic_id,
                "score": score,
                "reason": self._get_recommendation_reason(topic_progress, score)
            })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:10]  # Return top 10
    
    @staticmethod
    def _get_recommendation_reason(progress: Dict, score: float) -> str:
        """Generate human-readable reason for recommendation."""
        completion = progress.get("completion_percentage", 0)
        quiz_score = progress.get("quiz_score", 0)
        
        if completion == 0:
            return "You haven't started this topic yet"
        elif completion < 50:
            return "You're making progress here"
        elif quiz_score < 70:
            return "You could improve your quiz score"
        else:
            return "Great progress! Keep going"
