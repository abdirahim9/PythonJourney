import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest  # For outlier detection
from sklearn.base import BaseEstimator, TransformerMixin  # For custom transformer
from mlflow.models import infer_signature

mlflow.set_tracking_uri("sqlite:///mlflow.db")

class OutlierRemover(BaseEstimator, TransformerMixin):
    """Custom transformer for outlier removal using IsolationForest on specified features."""
    def __init__(self, features, contamination=0.1, random_state=42):
        self.features = features
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(contamination=contamination, random_state=random_state)

    def fit(self, X, y=None):
        self.model.fit(X[self.features])
        return self

    def transform(self, X):
        pred = self.model.predict(X[self.features])
        return X[pred == 1].copy()  # Return non-outliers, copy to avoid SettingWithCopyWarning

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
    """Extends Simulator with preprocessing pipelines."""
    def generate_raw_data(self, introduce_missing=False, introduce_outliers=False):
        """Generate raw dataframe with potential issues."""
        data = []
        for s in self.signals:
            mean = np.mean(s.data)
            var = np.var(s.data)
            label = 'low' if var < 50 else 'medium' if var < 150 else 'high'
            data.append({'mean': mean, 'var': var, 'label': label})
        df = pd.DataFrame(data)
        if introduce_missing:
            df.loc[np.random.choice(df.index, size=2), 'var'] = np.nan  # Introduce NaNs
        if introduce_outliers:
            df.loc[np.random.choice(df.index), 'var'] *= 10  # Amplify outliers
        return df

    def build_preprocessing_pipeline(self):
        """Build automated pipeline for scaling, encoding, cleaning."""
        num_features = ['mean', 'var']
        cat_features = ['label']
        # Outlier removal as a separate step on num_features
        outlier_step = ('outlier_remover', OutlierRemover(features=num_features, contamination=0.1, random_state=42))
        # Main pipeline: outlier removal first (applies to whole DF), then ColumnTransformer
        preprocessor = Pipeline([
            outlier_step,
            ('transformer', ColumnTransformer([
                ('num', Pipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler())
                ]), num_features),
                ('cat', Pipeline([
                    ('encoder', OneHotEncoder(handle_unknown='ignore'))
                ]), cat_features)
            ]))
        ])
        return preprocessor

    def apply_pipeline(self, df, preprocessor):
        """Apply pipeline and log to MLflow."""
        try:
            processed_data = preprocessor.fit_transform(df)
            # Log pipeline
            with mlflow.start_run():
                mlflow.sklearn.log_model(preprocessor, "preprocessor")
            return processed_data
        except Exception as e:
            print(f"Pipeline error: {e}")
            return None

def main():
    sim = MLSimulator()
    # Add signals with varying std
    for i in range(20):
        std = np.random.choice([3, 10, 20])
        length = np.random.randint(50, 200)
        sim.add_signal(Signal(length=length, std=std))
    # Generate varied data
    df_clean = sim.generate_raw_data()
    df_missing = sim.generate_raw_data(introduce_missing=True)
    df_outliers = sim.generate_raw_data(introduce_outliers=True)
    preprocessor = sim.build_preprocessing_pipeline()
    # Test robustness
    processed_clean = sim.apply_pipeline(df_clean, preprocessor)
    processed_missing = sim.apply_pipeline(df_missing, preprocessor)
    processed_outliers = sim.apply_pipeline(df_outliers, preprocessor)
    print("Processed Clean Shape:", processed_clean.shape if processed_clean is not None else "Error")
    print("Processed Missing Shape:", processed_missing.shape if processed_missing is not None else "Error")
    print("Processed Outliers Shape:", processed_outliers.shape if processed_outliers is not None else "Error")

if __name__ == "__main__":
    main()