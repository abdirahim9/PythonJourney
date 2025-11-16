import numpy as np
import pandas as pd
import mlflow
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import os
import subprocess  # For DVC commands

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
    """Extends Simulator with PCA reduction."""
    def generate_raw_data(self):
        """Generate balanced raw dataframe."""
        data = []
        for std in [3, 10, 20]:
            for _ in range(10):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                label = 0 if std == 3 else 1 if std == 10 else 2  # Numeric labels for classification
                data.append({'mean': mean, 'var': var, 'label': label})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def apply_pca(self, df, n_components=1):
        """Apply PCA and analyze impact."""
        features = df[['mean', 'var']]
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=n_components))
        ])
        reduced = pipeline.fit_transform(features)
        explained_variance = pipeline.named_steps['pca'].explained_variance_ratio_
        # Version with DVC
        reduced_df = pd.DataFrame(reduced, columns=[f'PC{i+1}' for i in range(n_components)])
        reduced_df.to_csv('reduced_data.csv', index=False)
        # Initialize DVC if not present
        if not os.path.exists('.dvc'):
            subprocess.run(['dvc', 'init', '--no-scm'], check=True)  # --no-scm if not using Git for DVC
        subprocess.run(['dvc', 'add', 'reduced_data.csv'], check=True)
        subprocess.run(['git', 'add', 'reduced_data.csv.dvc'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Versioned reduced dataset with DVC'], check=True)
        # Analyze impact: Compare classifier F1 on original vs. reduced
        X_orig = features
        y = df['label']
        X_train_orig, X_test_orig, y_train, y_test = train_test_split(X_orig, y, test_size=0.2, random_state=42)
        clf_orig = RandomForestClassifier(random_state=42).fit(X_train_orig, y_train)
        f1_orig = f1_score(y_test, clf_orig.predict(X_test_orig), average='weighted')
        X_reduced = reduced_df
        X_train_red, X_test_red, y_train, y_test = train_test_split(X_reduced, y, test_size=0.2, random_state=42)
        clf_red = RandomForestClassifier(random_state=42).fit(X_train_red, y_train)
        f1_red = f1_score(y_test, clf_red.predict(X_test_red), average='weighted')
        # Log to MLflow
        with mlflow.start_run():
            mlflow.log_param("n_components", n_components)
            mlflow.log_metric("explained_variance", sum(explained_variance))
            mlflow.log_metric("f1_original", f1_orig)
            mlflow.log_metric("f1_reduced", f1_red)
        return reduced_df, explained_variance, f1_orig, f1_red

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()
    reduced_df, variance, f1_orig, f1_red = sim.apply_pca(df)
    print("Explained Variance:", variance)
    print("Original F1:", f1_orig, "Reduced F1:", f1_red)
    print("Reduced data versioned with DVC.")

if __name__ == "__main__":
    main()