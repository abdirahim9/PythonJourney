import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import IsolationForest
from sklearn.base import BaseEstimator, TransformerMixin
from mlflow.models import infer_signature

mlflow.set_tracking_uri("sqlite:///mlflow.db")

class OutlierRemover(BaseEstimator, TransformerMixin):
    """Custom transformer for outlier removal using IsolationForest on specified features."""
    def __init__(self, features, contamination=0.05, random_state=42):
        self.features = features
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(contamination=contamination, random_state=random_state)

    def fit(self, X, y=None):
        self.model.fit(X[self.features])
        return self

    def transform(self, X):
        pred = self.model.predict(X[self.features])
        return X[pred == 1].copy()

class Signal:
    _counter = 0
    def __init__(self, length, std=10):
        np.random.seed(42 + Signal._counter)
        self.data = np.random.normal(0, std, length)
        Signal._counter += 1

class Simulator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

class MLSimulator(Simulator):
    """Extends Simulator with model embedding."""
    def generate_raw_data(self):
        """Generate balanced raw dataframe for classification."""
        data = []
        for class_type, std in [('low', 3), ('medium', 10), ('high', 20)]:
            for _ in range(10):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                label = class_type
                data.append({'mean': mean, 'var': var, 'label': label})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def build_preprocessor(self):
        """Build preprocessor from Day 48, focused on features only."""
        num_features = ['mean', 'var']
        preprocessor = Pipeline([
            ('transformer', ColumnTransformer([
                ('num', Pipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler())
                ]), num_features)
            ]))
        ])
        return preprocessor

    def train_and_embed_model(self, X, y):
        """Train and embed tuned model for real-time use."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        remover = OutlierRemover(features=['mean', 'var'], contamination=0.05, random_state=42)
        remover.fit(X_train)
        pred_train = remover.model.predict(X_train[['mean', 'var']])
        X_train_clean = X_train[pred_train == 1]
        y_train_clean = y_train[pred_train == 1]
        pred_test = remover.model.predict(X_test[['mean', 'var']])
        X_test_clean = X_test[pred_test == 1]
        y_test_clean = y_test[pred_test == 1]
        preprocessor = self.build_preprocessor()
        full_pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        param_grid = {
            'classifier__n_estimators': [10, 50, 100],
            'classifier__max_depth': [None, 5, 10]
        }
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        grid_search = GridSearchCV(full_pipeline, param_grid, cv=cv, scoring='f1_weighted')
        grid_search.fit(X_train_clean, y_train_clean)
        self.embedded_model = grid_search.best_estimator_
        # Test integration
        y_pred = self.embedded_model.predict(X_test_clean)
        f1 = f1_score(y_test_clean, y_pred, average='weighted')
        return f1

    def real_time_decision(self, new_mean, new_var):
        """Use embedded model for real-time prediction and adaptation."""
        if self.embedded_model is None:
            print("Model not embedded.")
            return None
        input_df = pd.DataFrame({'mean': [new_mean], 'var': [new_var]})
        prediction = self.embedded_model.predict(input_df)[0]
        # Adaptive signal generation example
        adapted_std = 3 if prediction == 'low' else 10 if prediction == 'medium' else 20
        return prediction, adapted_std

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()
    X = df[['mean', 'var']]
    y = df['label']
    integration_f1 = sim.train_and_embed_model(X, y)
    print("Integration Test F1:", integration_f1)
    # Real-time simulation
    new_mean, new_var = 0.5, 100.0
    prediction, adapted_std = sim.real_time_decision(new_mean, new_var)
    print("Real-Time Prediction:", prediction, "Adapted Std:", adapted_std)
    # Ideate features
    print("Novel Feature Idea: Dynamic Difficulty - Increase simulation complexity if 'high' predicted, e.g., add noise based on prediction confidence.")

if __name__ == "__main__":
    main()