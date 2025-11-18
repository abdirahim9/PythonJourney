import numpy as np
import pandas as pd
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight  # For weighting

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
    """Extends Simulator with bias monitoring."""
    def generate_raw_data(self, imbalance_ratio=0.8):
        """Generate imbalanced raw dataframe (e.g., 80% class 0)."""
        data = []
        for std, count in [(3, int(30 * imbalance_ratio)), (10, int(30 * (1 - imbalance_ratio) / 2)), (20, int(30 * (1 - imbalance_ratio) / 2))]:
            for _ in range(count):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                label = 0 if std == 3 else 1 if std == 10 else 2
                group = 0 if mean < 0 else 1  # Protected attribute (e.g., group based on mean)
                data.append({'mean': mean, 'var': var, 'label': label, 'group': group})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def train_with_weighting(self, df):
        """Train with class weighting for imbalance."""
        X = df[['mean', 'var']]
        y = df['label']
        class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
        class_weights_dict = dict(enumerate(class_weights))
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(class_weight=class_weights_dict, random_state=42))
        ])
        pipeline.fit(X_train, y_train)
        f1 = f1_score(y_test, pipeline.predict(X_test), average='weighted')
        self.model = pipeline
        return f1

    def compute_disparate_impact(self, df, predictions):
        """Compute fairness metric (disparate impact on group)."""
        df['prediction'] = predictions
        privileged = df[df['group'] == 1]['prediction'].mean()
        unprivileged = df[df['group'] == 0]['prediction'].mean()
        disparate_impact = unprivileged / privileged if privileged > 0 else 0
        return disparate_impact

    def monitor_bias(self, df):
        """Monitor bias with logging."""
        if self.model is None:
            print("Model not trained.")
            return None
        predictions = self.model.predict(df[['mean', 'var']])
        disparate_impact = self.compute_disparate_impact(df, predictions)
        # Log to MLflow
        with mlflow.start_run():
            mlflow.log_metric("disparate_impact", disparate_impact)
        return disparate_impact

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()
    train_f1 = sim.train_with_weighting(df)
    print("Training F1 with Weighting:", train_f1)
    disparate_impact = sim.monitor_bias(df)
    print("Disparate Impact:", disparate_impact)

if __name__ == "__main__":
    main()