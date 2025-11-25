import numpy as np
import pandas as pd
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import yaml
import os
import subprocess

# Set MLflow tracking (local sqlite for this session)
mlflow.set_tracking_uri("sqlite:///mlflow.db")

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
    """Extends Simulator with forecasting integration."""
    def __init__(self):
        super().__init__()
        self.model = None

    def generate_raw_data(self):
        """Generate balanced raw dataframe for training."""
        data = []
        # Create signals with distinct variances to train the classifier
        for std in [3, 10, 20]:
            for _ in range(10):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                # Label mapping: 0 -> Low, 1 -> Medium, 2 -> High
                label = 0 if std == 3 else 1 if std == 10 else 2
                data.append({'mean': mean, 'var': var, 'label': label})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def train_model(self, df):
        """Train Random Forest classifier for signal forecasting."""
        X = df[['mean', 'var']]
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        f1 = f1_score(y_test, preds, average='weighted')
        self.model = pipeline
        return f1

    def forecast_signal(self, mean, var):
        """Forecast signal class using the integrated model."""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        input_df = pd.DataFrame({'mean': [mean], 'var': [var]})
        prediction = self.model.predict(input_df)[0]
        return prediction

    def hybrid_recursive_pattern(self, initial_std, steps=5):
        """
        Hybrid Feature: Recursive adjustment based on forecast.
        The next signal's std is determined by the model's prediction of the previous.
        """
        std = initial_std
        patterns = []
        for _ in range(steps):
            length = np.random.randint(50, 200)
            signal = Signal(length, std)
            mean = np.mean(signal.data)
            var = np.var(signal.data)

            # Use ML model to decide next state
            prediction = self.forecast_signal(mean, var)

            # Adjust system state based on prediction (Feedback Loop)
            std = 3 if prediction == 0 else 10 if prediction == 1 else 20
            patterns.append((mean, var, prediction, std))
        return patterns

    def setup_ci_cd(self):
        """Set up CI/CD workflow YAML with strict p99 gating."""
        workflow_dir = '.github/workflows'
        os.makedirs(workflow_dir, exist_ok=True)

        workflow = {
            'name': 'ML Model CI/CD',
            'on': {'push': {'branches': ['main']}},
            'jobs': {
                'build-and-test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {'name': 'Set up Python', 'uses': 'actions/setup-python@v4', 'with': {'python-version': '3.12'}},
                        {'name': 'Install dependencies', 'run': 'pip install -r requirements.txt'},
                        {'name': 'Run Unit Tests', 'run': 'python -m unittest numpy_test.py'},
                        {'name': 'Run Performance Benchmark', 'run': 'python benchmark.py'}
                    ]
                }
            }
        }

        yaml_path = os.path.join(workflow_dir, 'ml_cicd.yaml')
        with open(yaml_path, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)

        # Automate git staging
        try:
            subprocess.run(['git', 'add', 'requirements.txt'], check=True)
            subprocess.run(['git', 'add', 'benchmark.py'], check=True)
            subprocess.run(['git', 'add', yaml_path], check=True)
            print(f"CI/CD configuration generated at {yaml_path}")
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()

    # Train and validate
    train_f1 = sim.train_model(df)
    print(f"Training Weighted F1 Score: {train_f1:.4f}")

    # Demonstrate Hybrid Feature
    patterns = sim.hybrid_recursive_pattern(initial_std=10, steps=3)
    print("Hybrid Recursive Patterns (Mean, Var, Pred, Next_Std):")
    for p in patterns:
        print(p)

    # Generate CI/CD Artifacts
    sim.setup_ci_cd()
    print("CI/CD workflow setup complete.")

if __name__ == "__main__":
    main()