import numpy as np
import pandas as pd
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight

# Set MLflow tracking to local sqlite
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
    """Extends Simulator with bias monitoring and imbalance handling."""
    def __init__(self):
        super().__init__()
        self.model = None

    def generate_raw_data(self, imbalance_ratio=0.8):
        """
        Generate imbalanced raw dataframe (80% class 0).
        'group' acts as a protected attribute.
        """
        data = []
        # FIX: Increased base count from 30 to 1000 to ensure minority classes have enough samples
        base_count = 1000
        
        for std, count in [(3, int(base_count * imbalance_ratio)), 
                           (10, int(base_count * (1 - imbalance_ratio) / 2)), 
                           (20, int(base_count * (1 - imbalance_ratio) / 2))]:
            for _ in range(count):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                
                label = 0 if std == 3 else 1 if std == 10 else 2
                # Synthetic protected attribute: 0 is unprivileged, 1 is privileged
                group = 0 if mean < 0 else 1 
                data.append({'mean': mean, 'var': var, 'label': label, 'group': group})
        
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def train_with_weighting(self, df):
        """Train Random Forest with 'balanced' class weights to handle imbalance."""
        X = df[['mean', 'var']]
        y = df['label']
        
        # Explicitly compute weights (optional, but good for tracking)
        weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
        print(f"Computed Class Weights: {weights}")

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            # 'balanced' mode automatically adjusts weights
            ('classifier', RandomForestClassifier(class_weight='balanced', random_state=42))
        ])
        
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        f1 = f1_score(y_test, preds, average='weighted')
        self.model = pipeline
        return f1

    def compute_disparate_impact(self, df, predictions):
        """
        Compute Disparate Impact (DI). 
        DI = P(Y=favorable | Unprivileged) / P(Y=favorable | Privileged)
        """
        df_temp = df.copy()
        df_temp['prediction'] = predictions
        
        # Assuming Class 0 is the "favorable" outcome we are monitoring for equity
        favorable_outcome = 0
        
        privileged_rate = df_temp[df_temp['group'] == 1]['prediction'].apply(lambda x: 1 if x==favorable_outcome else 0).mean()
        unprivileged_rate = df_temp[df_temp['group'] == 0]['prediction'].apply(lambda x: 1 if x==favorable_outcome else 0).mean()
        
        if privileged_rate == 0:
            return 0.0
        
        disparate_impact = unprivileged_rate / privileged_rate
        return disparate_impact

    def monitor_bias(self, df):
        """Monitor bias with logging to MLflow."""
        if self.model is None:
            print("Model not trained.")
            return None
        
        predictions = self.model.predict(df[['mean', 'var']])
        di = self.compute_disparate_impact(df, predictions)
        
        with mlflow.start_run():
            mlflow.log_metric("disparate_impact", di)
            print(f"Logged Disparate Impact: {di:.4f}")
        
        return di

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data(imbalance_ratio=0.8)
    
    # Train
    train_f1 = sim.train_with_weighting(df)
    print(f"Training F1 with Weighting: {train_f1:.4f}")
    
    # Monitor
    impact = sim.monitor_bias(df)
    print(f"Disparate Impact: {impact:.4f}")

if __name__ == "__main__":
    main()