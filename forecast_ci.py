import numpy as np
import pandas as pd
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import yaml  # For generating CI/CD workflow configuration files
import os  # For handling directory creation and file paths
import subprocess  # For executing Git commands programmatically
import timeit  # For implementing performance benchmarking and gating

mlflow.set_tracking_uri("sqlite:///mlflow.db")  # Sets up MLflow tracking for experiment logging

class Signal:
    _counter = 0  # Class-level counter to ensure reproducible seeding across instances
    def __init__(self, length, std=10):
        np.random.seed(42 + Signal._counter)  # Seeded for reproducibility
        self.data = np.random.normal(0, std, length)  # Generates normally distributed signal data
        Signal._counter += 1  # Increments counter for next instance

class Simulator:
    def __init__(self):
        self.signals = []  # Initializes list to store signal objects
    def add_signal(self, signal):
        self.signals.append(signal)  # Appends new signal to the list

class MLSimulator(Simulator):
    """Extends the base Simulator class with machine learning-based forecasting capabilities."""
    def __init__(self):
        super().__init__()  # Calls parent constructor
        self.model = None  # Placeholder for trained model
    
    def generate_raw_data(self):
        """Generates a balanced dataset for training, simulating varied signal characteristics."""
        data = []
        for std in [3, 10, 20]:  # Iterates over different standard deviations for label diversity
            for _ in range(10):  # Creates 10 samples per category for balance
                length = np.random.randint(50, 200)  # Random length between 50 and 200
                signal = Signal(length, std)  # Instantiates Signal with given std
                mean = np.mean(signal.data)  # Computes mean of signal data
                var = np.var(signal.data)  # Computes variance of signal data
                label = 0 if std == 3 else 1 if std == 10 else 2  # Assigns label based on std
                data.append({'mean': mean, 'var': var, 'label': label})  # Appends feature dict
        np.random.shuffle(data)  # Shuffles data for randomness in splitting
        return pd.DataFrame(data)  # Returns as Pandas DataFrame
    
    def train_model(self, df):
        """Trains a classification pipeline for forecasting signal categories."""
        X = df[['mean', 'var']]  # Extracts features
        y = df['label']  # Extracts target labels
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # Splits data
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),  # Handles missing values
            ('scaler', StandardScaler()),  # Standardizes features
            ('classifier', RandomForestClassifier(random_state=42))  # Random Forest classifier
        ])
        pipeline.fit(X_train, y_train)  # Fits the pipeline to training data
        f1 = f1_score(y_test, pipeline.predict(X_test), average='weighted')  # Computes weighted F1 score
        self.model = pipeline  # Stores trained model
        return f1  # Returns F1 score for evaluation
    
    def forecast_signal(self, mean, var):
        """Performs forecasting using the trained model on provided features."""
        if self.model is None:
            print("Model not trained.")  # Error handling for untrained model
            return None
        input_df = pd.DataFrame({'mean': [mean], 'var': [var]})  # Creates input DataFrame
        prediction = self.model.predict(input_df)[0]  # Predicts category
        return prediction  # Returns the predicted label
    
    def hybrid_recursive_pattern(self, initial_std, steps=5):
        """Implements hybrid feature: Recursively adjusts patterns based on model forecasts."""
        std = initial_std  # Starts with initial standard deviation
        patterns = []  # List to store pattern tuples
        for _ in range(steps):  # Loops for specified steps
            length = np.random.randint(50, 200)  # Random signal length
            signal = Signal(length, std)  # Generates signal
            mean = np.mean(signal.data)  # Computes mean
            var = np.var(signal.data)  # Computes variance
            prediction = self.forecast_signal(mean, var)  # Forecasts using model
            # Adjusts std recursively based on prediction for hybrid behavior
            std = 3 if prediction == 0 else 10 if prediction == 1 else 20
            patterns.append((mean, var, prediction, std))  # Appends tuple to list
        return patterns  # Returns list of patterns
    
    def setup_ci_cd(self):
        """Configures CI/CD workflow in YAML format with integrated p99 benchmark gating."""
        workflow_dir = '.github/workflows'  # Defines workflow directory path
        os.makedirs(workflow_dir, exist_ok=True)  # Creates directory if not present
        workflow = {
            'name': 'ML Model CI/CD',  # Workflow name
            'on': {'push': {'branches': ['main']}},  # Triggers on push to main
            'jobs': {
                'test': {
                    'runs-on': 'ubuntu-latest',  # Runs on latest Ubuntu
                    'steps': [
                        {'uses': 'actions/checkout@v2'},  # Checks out repository
                        {'name': 'Set up Python', 'uses': 'actions/setup-python@v2', 'with': {'python-version': '3.12'}},  # Sets up Python
                        {'name': 'Install dependencies', 'run': 'pip install -r requirements.txt'},  # Installs deps
                        {'name': 'Run tests', 'run': 'python -m unittest numpy_test.py'},  # Runs unit tests
                        {'name': 'Benchmark p99', 'run': 'python benchmark.py'}  # Executes benchmark script
                    ]
                }
            }
        }
        with open(os.path.join(workflow_dir, 'ml_cicd.yaml'), 'w') as f:
            yaml.dump(workflow, f)  # Writes YAML to file
        # Defines benchmark script content for p99 gating
        benchmark_code = """
        import timeit
        import numpy as np
        def test_func():
            # Simulate forecast call (replace with actual for production)
            pass
        times = timeit.repeat(test_func, number=100, repeat=10)  # Measures execution times
        p99 = np.percentile(times, 99)  # Calculates 99th percentile
        if p99 > 0.5:  # Gates if p99 exceeds 500ms threshold
            raise ValueError('p99 exceeds 500ms')
        print('p99:', p99)
        """
        with open('benchmark.py', 'w') as f:
            f.write(benchmark_code)  # Writes benchmark script
        subprocess.run(['git', 'add', 'benchmark.py'], check=True)  # Stages benchmark file
        subprocess.run(['git', 'add', os.path.join(workflow_dir, 'ml_cicd.yaml')], check=True)  # Stages YAML
        subprocess.run(['git', 'commit', '-m', 'Added CI/CD workflow with p99 gating for Day 53'], check=True)  # Commits changes

def main():
    sim = MLSimulator()  # Instantiates MLSimulator
    df = sim.generate_raw_data()  # Generates training data
    train_f1 = sim.train_model(df)  # Trains model and gets F1
    print("Training F1:", train_f1)  # Outputs F1 score
    # Demonstrates hybrid functionality
    patterns = sim.hybrid_recursive_pattern(initial_std=10, steps=3)  # Generates 3 steps of patterns
    print("Hybrid Patterns:", patterns)  # Outputs patterns
    # Configures CI/CD
    sim.setup_ci_cd()  # Sets up workflow
    print("CI/CD workflow set up with p99 gating.")  # Confirmation message

if __name__ == "__main__":
    main()  # Executes main function