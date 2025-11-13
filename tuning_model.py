import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import GridSearchCV, train_test_split, StratifiedKFold
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
    _counter = 0  # Class-level counter for varying seeds
    def __init__(self, length, std=10):
        np.random.seed(42 + Signal._counter)  # Vary seed per instance
        self.data = np.random.normal(0, std, length)
        Signal._counter += 1

class Simulator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

class MLSimulator(Simulator):
    """Extends Simulator with tuning and CV."""
    def generate_raw_data(self):
        """Generate balanced raw dataframe for classification."""
        data = []
        # Ensure balanced classes: 10 per class
        for class_type, std in [('low', 3), ('medium', 10), ('high', 20)]:
            for _ in range(10):  # 10 per class
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                label = class_type
                data.append({'mean': mean, 'var': var, 'label': label})
        np.random.shuffle(data)  # Shuffle to mix
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

    def baseline_model(self, X_train, y_train):
        """Train baseline RandomForest."""
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        return model

    def tune_model(self, X_train, y_train, preprocessor):
        """Tune with GridSearchCV using StratifiedKFold."""
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
        grid_search.fit(X_train, y_train)
        return grid_search

    def critique_improvement(self, baseline_score, tuned_score):
        """Critique performance."""
        improvement = tuned_score - baseline_score
        print(f"Baseline F1: {baseline_score:.3f}, Tuned F1: {tuned_score:.3f}, Improvement: {improvement:.3f} ({improvement/baseline_score*100:.1f}%)")
        return improvement > 0

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()  # Now balanced
    X = df[['mean', 'var']]
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    preprocessor = sim.build_preprocessor()
    # Outlier removal as pre-step on train
    num_features = ['mean', 'var']
    remover = OutlierRemover(features=num_features, contamination=0.05, random_state=42)
    remover.fit(X_train)
    pred_train = remover.model.predict(X_train[num_features])
    X_train_clean = X_train[pred_train == 1]
    y_train_clean = y_train[pred_train == 1]
    # Baseline on clean train
    baseline = sim.baseline_model(X_train_clean, y_train_clean)
    # Transform test (in practice, outliers in test might be kept, but for consistency)
    pred_test = remover.model.predict(X_test[num_features])
    X_test_clean = X_test[pred_test == 1]
    y_test_clean = y_test[pred_test == 1]
    y_pred_baseline = baseline.predict(X_test_clean)
    baseline_f1 = f1_score(y_test_clean, y_pred_baseline, average='weighted')
    # Tuned on clean train
    tuned = sim.tune_model(X_train_clean, y_train_clean, preprocessor)
    y_pred_tuned = tuned.predict(X_test)
    tuned_f1 = f1_score(y_test, y_pred_tuned, average='weighted')
    # Critique
    improvement = sim.critique_improvement(baseline_f1, tuned_f1)
    print("Tuning improved model:", improvement)
    print("Best Params:", tuned.best_params_)
    # MLflow
    with mlflow.start_run():
        mlflow.log_params(tuned.best_params_)
        mlflow.log_metric("baseline_f1", baseline_f1)
        mlflow.log_metric("tuned_f1", tuned_f1)
        signature = infer_signature(X_train_clean, tuned.predict(X_train_clean))
        mlflow.sklearn.log_model(tuned.best_estimator_, name="tuned_classifier", signature=signature, input_example=X_train_clean.iloc[:1])

if __name__ == "__main__":
    main()