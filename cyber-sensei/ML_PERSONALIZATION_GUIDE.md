# Neural Network Personalization Implementation Guide

## Overview

This guide details how to implement and integrate the neural network personalization system into Cyber-Sensei.

## Phase 1: Data Collection & Tracking

### 1.1 Log User Interactions

Update knowledge router to track user interactions:

```python
from app.ml_personalization import user_manager, UserInteraction

@router.post("/api/learning/{username}/submit-quiz")
async def submit_quiz(username: str, body: dict):
    # ... existing quiz logic ...
    
    # Log interaction for ML training
    interaction = UserInteraction(
        user_id=username,
        interaction_type="quiz_complete",
        topic_id=body.get("topic_id"),
        score=score,
        duration_seconds=body.get("duration")
    )
    user_manager.log_interaction(interaction)
```

### 1.2 Track Resource Views

```python
@router.get("/api/knowledge-base/{doc_id}")
async def get_document(doc_id: int):
    # ... existing logic ...
    
    # Log view interaction
    interaction = UserInteraction(
        user_id="current_user",
        interaction_type="resource_view",
        topic_id=doc_id,
        duration_seconds=time_spent
    )
    user_manager.log_interaction(interaction)
```

### 1.3 Database Schema for Interactions

Add to `models.py`:

```python
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True)
    interaction_type = Column(String)  # quiz_complete, resource_view, etc.
    topic_id = Column(Integer)
    score = Column(Float, nullable=True)  # For quizzes
    duration_seconds = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_user_interactions', 'user_id', 'timestamp'),
    )
```

## Phase 2: Model Architecture

### 2.1 Recommendation Model

**Input Features:**
- User's topic history
- Quiz scores per topic
- Time spent per topic
- Learning pace
- Previous recommendations accepted

**Architecture:**
```
Input Layer (20 features)
  ↓
Dense (128 units, ReLU)
  ↓
Dropout (0.3)
  ↓
Dense (64 units, ReLU)
  ↓
Dropout (0.3)
  ↓
Dense (32 units, ReLU)
  ↓
Output Layer (num_topics units, Softmax)
```

**Output:** Probability distribution over topics (sum = 1.0)

### 2.2 Difficulty Prediction Model

**Input Features:**
- Current proficiency on topic
- Quiz attempt count
- Average score trend
- Time since last attempt

**Architecture:**
```
Input Layer (4 features)
  ↓
Dense (32 units, ReLU)
  ↓
Dense (16 units, ReLU)
  ↓
Output Layer (3 units, Softmax)  # [easy, medium, hard]
```

**Output:** Difficulty recommendation + success probability

## Phase 3: Training Pipeline

### 3.1 Data Preparation

```python
# train_model.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from app.ml_personalization import training_pipeline

# Collect data
training_data = training_pipeline.collect_training_data(days=90)

# Convert to DataFrame
df = pd.DataFrame(training_data['interactions'])

# Feature engineering
df['time_normalized'] = StandardScaler().fit_transform(df[['duration_seconds']])
df['score_trend'] = df.groupby('user_id')['score'].pct_change()

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df.drop('topic_id', axis=1),
    df['topic_id'],
    test_size=0.2,
    random_state=42
)
```

### 3.2 Model Training

```python
import tensorflow as tf

# Build model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_dim=20),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(num_topics, activation='softmax')
])

# Compile
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
history = model.fit(
    X_train, y_train,
    batch_size=32,
    epochs=100,
    validation_data=(X_test, y_test),
    callbacks=[
        tf.keras.callbacks.EarlyStopping(patience=10),
        tf.keras.callbacks.ReduceLROnPlateau()
    ]
)

# Save model
model.save('models/recommendation_model.h5')
```

### 3.3 Model Evaluation

```python
# Evaluate on test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy:.2%}")

# Get predictions
predictions = model.predict(X_test)
top_3_topics = np.argsort(predictions, axis=1)[:, -3:][:, ::-1]

# Calculate recommendation acceptance rate
recommendation_acceptance = (y_test in top_3_topics).mean()
print(f"Top-3 Recommendation Acceptance: {recommendation_acceptance:.2%}")
```

## Phase 4: Integration with API

### 4.1 Add Recommendation Endpoint

```python
from app.ml_personalization import personalization_engine

@router.get("/api/user/{username}/recommendations")
async def get_recommendations(username: str, count: int = 3):
    """Get personalized topic recommendations."""
    recommendations = personalization_engine.recommend_next_topics(
        user_id=username,
        num_recommendations=count
    )
    return {"recommendations": recommendations}
```

### 4.2 Add Difficulty Suggestion Endpoint

```python
@router.get("/api/learning/topic/{topic_id}/difficulty/suggest")
async def suggest_difficulty(topic_id: int, username: str):
    """Get suggested quiz difficulty based on proficiency."""
    difficulty = personalization_engine.suggest_quiz_difficulty(
        user_id=username,
        topic_id=topic_id
    )
    return difficulty
```

### 4.3 Add Learning Path Endpoint

```python
@router.get("/api/user/{username}/learning-path")
async def get_learning_path(username: str):
    """Get adaptive personalized learning path."""
    path = personalization_engine.adapt_learning_path(username)
    return {"learning_path": path}
```

## Phase 5: Deployment & Monitoring

### 5.1 Model Serving

Use FastAPI for model serving:

```python
from fastapi import FastAPI
import tensorflow as tf

app = FastAPI()
model = tf.keras.models.load_model('models/recommendation_model.h5')

@app.post("/predict")
async def predict(features: dict):
    input_data = np.array([list(features.values())])
    predictions = model.predict(input_data)
    return {"predictions": predictions.tolist()}
```

Or use TensorFlow Serving:

```bash
docker run -t --rm -p 8501:8501 \
  -v "$(pwd)/models/recommendation_model:/models/recommendation_model" \
  tensorflow/serving
```

### 5.2 Training Schedule

Set up periodic retraining:

```python
# Celery task for nightly training
@celery_app.task(name="ml.train_personalization_model")
def train_model_task():
    """Nightly model retraining."""
    data = training_pipeline.collect_training_data(days=30)
    processed = training_pipeline.preprocess_data(data)
    training_pipeline.train_model(processed)
    
    # Evaluate
    metrics = training_pipeline.evaluate_model(processed)
    logger.info(f"Model training complete. Accuracy: {metrics['accuracy']}")

# Schedule with celery beat
from celery.schedules import crontab

app.conf.beat_schedule = {
    'train-model-nightly': {
        'task': 'ml.train_personalization_model',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}
```

### 5.3 Model Monitoring

```python
class ModelMonitor:
    def log_prediction(self, user_id: str, recommendation: int, accepted: bool):
        """Log model prediction and user acceptance."""
        # Track model performance over time
        
    def calculate_drift(self):
        """Detect if user behavior has shifted (data drift)."""
        # Trigger retraining if drift detected
        
    def get_metrics(self):
        """Get current model performance metrics."""
        return {
            "accuracy": 0.87,
            "recommendation_acceptance": 0.72,
            "user_satisfaction": 4.2,  # 1-5 rating
            "data_drift_score": 0.15  # 0-1, higher = more drift
        }
```

## Phase 6: User Feedback

### 6.1 Feedback Collection

```python
@router.post("/api/user/{username}/feedback/recommendation")
async def provide_recommendation_feedback(username: str, body: dict):
    """User rates recommendation quality."""
    # body: {"topic_id": 5, "helpful": true, "rating": 4}
    
    user_manager.log_interaction(
        UserInteraction(
            user_id=username,
            interaction_type="feedback_recommendation",
            topic_id=body["topic_id"],
            metadata={"rating": body.get("rating"), "helpful": body.get("helpful")}
        )
    )
```

### 6.2 Learning Style Detection

Track user learning style preferences:

```python
def detect_learning_style(user_id: str):
    """Detect user's preferred learning style."""
    profile = user_manager.get_user_profile(user_id)
    
    # Analyze interaction patterns
    if video_views > text_reads * 2:
        return "visual"
    elif practice_attempts > quiz_attempts:
        return "kinesthetic"
    else:
        return "mixed"
```

## Implementation Checklist

- [ ] Add UserInteraction model to database
- [ ] Create data collection endpoints
- [ ] Implement feature engineering pipeline
- [ ] Build and train initial model
- [ ] Deploy model serving endpoint
- [ ] Integrate recommendations into API
- [ ] Set up scheduled retraining
- [ ] Implement monitoring and logging
- [ ] Add user feedback collection
- [ ] Monitor model drift and performance

## Testing

```bash
# Run model tests
pytest tests/test_ml_personalization.py

# Test recommendations
curl http://localhost:8000/api/user/testuser/recommendations?count=5

# Test difficulty suggestion
curl http://localhost:8000/api/learning/topic/1/difficulty/suggest?username=testuser
```

## References

- [TensorFlow Keras](https://www.tensorflow.org/guide/keras)
- [Scikit-learn Preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Recommendation Systems](https://developers.google.com/machine-learning/recommendation)
- [Data Drift Detection](https://en.wikipedia.org/wiki/Concept_drift)
