import os
import sys
import subprocess

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

# Configure MLflow to use a local SQLite DB
mlflow.set_tracking_uri("sqlite:///mlflow.db")


class Signal:
    _counter = 0

    def __init__(self, length, std: float = 10.0):
        # Deterministic but changing seed across signals
        np.random.seed(42 + Signal._counter)
        self.data = np.random.normal(0.0, std, length)
        Signal._counter += 1


class Simulator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal: Signal) -> None:
        self.signals.append(signal)


class MLSimulator(Simulator):
    """Extends Simulator with forecasting integration."""

    def __init__(self):
        super().__init__()
        self.model: Pipeline | None = None

    def generate_raw_data(self) -> pd.DataFrame:
        """Generate balanced raw dataframe with mean/var and label."""
        data = []
        for std in [3, 10, 20]:
            for _ in range(10):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = float(np.mean(signal.data))
                var = float(np.var(signal.data))
                label = 0 if std == 3 else 1 if std == 10 else 2
                data.append({"mean": mean, "var": var, "label": label})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def train_model(self, df: pd.DataFrame) -> float:
        """Train classifier and return weighted F1 on holdout set."""
        X = df[["mean", "var"]]
        y = df["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="mean")),
                ("scaler", StandardScaler()),
                ("classifier", RandomForestClassifier(random_state=42)),
            ]
        )

        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        f1 = f1_score(y_test, preds, average="weighted")
        self.model = pipeline

        # Log metrics and params to MLflow
        with mlflow.start_run(run_name="ml_simulator_ci"):
            mlflow.log_param("model_type", "RandomForestClassifier")
            mlflow.log_param("features", ["mean", "var"])
            mlflow.log_metric("f1_weighted", float(f1))

        return float(f1)

    def forecast_signal(self, mean: float, var: float) -> int:
        """Forecast label using trained model."""
        if self.model is None:
            raise ValueError("Model not trained.")
        input_df = pd.DataFrame({"mean": [mean], "var": [var]})
        prediction = int(self.model.predict(input_df)[0])
        return prediction

    def hybrid_recursive_pattern(self, initial_std: float, steps: int = 5):
        """
        Hybrid feature: recursive adjustment based on model forecast.

        Returns list of tuples: (mean, var, prediction, std_after_prediction)
        """
        std = initial_std
        patterns = []
        for _ in range(steps):
            length = np.random.randint(50, 200)
            signal = Signal(length, std)
            mean = float(np.mean(signal.data))
            var = float(np.var(signal.data))
            prediction = self.forecast_signal(mean, var)
            # Map prediction class back to std
            std = 3 if prediction == 0 else 10 if prediction == 1 else 20
            patterns.append((mean, var, prediction, std))
        return patterns

    def setup_ci_cd(self) -> None:
        """
        Set up CI/CD workflow YAML with F1 and p99 gating.

        - Writes .github/workflows/ml_cicd.yaml
        - When NOT running in CI (no CI env var), also auto-commits the workflow,
          requirements.txt, and benchmark.py for your Day 53 narrative.
        """
        workflow_dir = ".github/workflows"
        os.makedirs(workflow_dir, exist_ok=True)

        workflow = {
            "name": "ML Model CI/CD",
            "on": {
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
                "workflow_dispatch": {},
            },
            "jobs": {
                "test-and-ml": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout repo", "uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v5",
                            "with": {"python-version": "3.12"},
                        },
                        {
                            "name": "Install dependencies",
                            "run": (
                                "python -m pip install --upgrade pip && "
                                "pip install -r requirements.txt && "
                                "pip install ruff mypy"
                            ),
                        },
                        {
                            "name": "Lint with ruff",
                            "run": "ruff check .",
                        },
                        {
                            "name": "Type check with mypy",
                            "run": "mypy .",
                        },
                        {
                            "name": "Run unit tests (discover)",
                            "run": "python -m unittest discover -s . -p 'test_*.py'",
                        },
                        {
                            "name": "Run ML pipeline with F1 gate",
                            "env": {"F1_THRESHOLD": "0.90"},
                            "run": "python forecast_ci.py",
                        },
                        {
                            "name": "Run p99 benchmark",
                            "env": {"P99_THRESHOLD": "0.050"},
                            "run": "python benchmark.py",
                        },
                    ],
                }
            },
        }

        workflow_path = os.path.join(workflow_dir, "ml_cicd.yaml")
        with open(workflow_path, "w", encoding="utf-8") as f:
            yaml.dump(workflow, f, sort_keys=False)

        # Only auto-commit when running locally (not in CI)
        if not os.getenv("CI"):
            try:
                subprocess.run(["git", "add", "requirements.txt"], check=False)
                subprocess.run(["git", "add", "benchmark.py"], check=False)
                subprocess.run(["git", "add", workflow_path], check=False)
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        "Added/updated CI/CD workflow, requirements, and benchmark for Day 53",
                    ],
                    check=False,
                )
            except Exception as e:
                print(f"Warning: git auto-commit failed: {e}", file=sys.stderr)


def main() -> None:
    sim = MLSimulator()

    # 1) Generate data and train model
    df = sim.generate_raw_data()
    train_f1 = sim.train_model(df)
    print("Training F1:", train_f1)

    # 2) F1 gate for CI (optional in local runs)
    threshold_str = os.getenv("F1_THRESHOLD", "").strip()
    if threshold_str:
        try:
            threshold = float(threshold_str)
        except ValueError:
            print(f"Invalid F1_THRESHOLD value: {threshold_str}", file=sys.stderr)
            sys.exit(1)

        if train_f1 < threshold:
            print(
                f"F1 gate FAILED: {train_f1:.4f} < threshold {threshold:.4f}",
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            print(
                f"F1 gate PASSED: {train_f1:.4f} >= threshold {threshold:.4f}",
            )

    # 3) Hybrid recursive patterns
    patterns = sim.hybrid_recursive_pattern(initial_std=10, steps=3)
    print("Hybrid Patterns:", patterns)

    # 4) Ensure CI/CD workflow exists and is updated
    sim.setup_ci_cd()
    print("CI/CD workflow set up with F1 + p99 gating.")


if __name__ == "__main__":
    main()
