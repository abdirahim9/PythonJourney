import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from lime.lime_tabular import LimeTabularExplainer
from mlflow.models import infer_signature

mlflow.set_tracking_uri("sqlite:///mlflow.db")  # Fix: Switch to SQLite backend for tracking

class Signal:
    def __init__(self, length, std=10):
        np.random.seed(42)
        self.data = np.random.normal(0, std, length)  # Variable std for diverse variances

class Simulator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

class MLSimulator(Simulator):
    """Extends Simulator with ML classification."""
    def train_classification(self, model_type='logistic'):
        """Train classification on signals to categorize types (low/medium/high variance)."""
        if not self.signals:
            print("No signals added.")
            return None, None
        # Generate features and labels
        data = []
        for s in self.signals:
            mean = np.mean(s.data)
            var = np.var(s.data)
            label = 'low' if var < 50 else 'medium' if var < 150 else 'high'  # Arbitrary thresholds for classes
            data.append({'mean': mean, 'var': var, 'label': label})
        df = pd.DataFrame(data)
        if len(df) < 3:  # Need at least one per class minimally
            print("Insufficient data for classification.")
            return None, None
        X = df[['mean', 'var']]
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        # Fix: Convert to NumPy arrays to avoid feature name warnings
        X_train_np = X_train.values
        X_test_np = X_test.values
        y_train_np = y_train.values
        y_test_np = y_test.values
        # Model selection
        if model_type == 'logistic':
            model = LogisticRegression()
        elif model_type == 'random_forest':
            model = RandomForestClassifier(n_estimators=50, random_state=42)
        else:
            raise ValueError("Invalid model_type")
        model.fit(X_train_np, y_train_np)
        y_pred = model.predict(X_test_np)
        # Metrics
        accuracy = accuracy_score(y_test_np, y_pred)
        precision = precision_score(y_test_np, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test_np, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test_np, y_pred, average='weighted', zero_division=0)
        metrics = {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1}
        # LIME for interpretability (explain one instance)
        explainer = LimeTabularExplainer(X_train_np, feature_names=['mean', 'var'], class_names=np.unique(y), mode="classification")
        exp = explainer.explain_instance(X_test_np[0], model.predict_proba)
        lime_exp = exp.as_list()
        # MLflow tracking
        with mlflow.start_run():
            mlflow.log_params({"model_type": model_type})
            mlflow.log_metrics(metrics)
            # Fix: Infer signature and provide input example
            signature = infer_signature(X_train_np, model.predict(X_train_np))
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                signature=signature,
                input_example=X_train_np[0:1],
                registered_model_name="classification_model"  # Fix: Use registered_model_name to align with deprecation guidance
            )
        return metrics, lime_exp

def main():
    sim = MLSimulator()
    # Add multiple signals with varying std for diverse classes
    for i in range(20):
        std = np.random.choice([3, 10, 20])  # Vars ~9, 100, 400 -> low, medium, high
        length = np.random.randint(50, 200)
        sim.add_signal(Signal(length=length, std=std))
    metrics_logistic, lime_logistic = sim.train_classification('logistic')
    metrics_rf, lime_rf = sim.train_classification('random_forest')
    print("Logistic Metrics:", metrics_logistic)
    print("Logistic LIME:", lime_logistic)
    print("RF Metrics:", metrics_rf)
    print("RF LIME:", lime_rf)

if __name__ == "__main__":
    main()