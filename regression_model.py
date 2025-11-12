import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

class Signal:
    def __init__(self, length):
        np.random.seed(42)
        self.data = np.random.normal(0, 10, length)  # Sample signal data: normal distribution

class Simulator:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

class MLSimulator(Simulator):
    """Extends Simulator with ML regression."""
    def train_regression(self):
        """Train regression on combined signals to predict values."""
        combined = np.concatenate([s.data for s in self.signals])
        if len(combined) < 2:
            print("Insufficient data for training.")
            return None, None, None
        # Create features: previous value as X, current as y (shift for forecasting)
        df = pd.DataFrame({'signal_data': combined})
        df['prev'] = df['signal_data'].shift(1).fillna(0)  # Simple lag feature
        X = df[['prev']]
        y = df['signal_data']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        importance = model.coef_  # Feature importance
        return mse, r2, importance

def main():
    sim = MLSimulator()
    signal1 = Signal(length=100)  # Larger for evaluation
    sim.add_signal(signal1)
    mse, r2, importance = sim.train_regression()
    print(f"MSE: {mse:.2f}, R²: {r2:.2f}, Feature Importance: {importance}")

if __name__ == "__main__":
    main()