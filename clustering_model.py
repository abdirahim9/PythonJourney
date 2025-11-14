import numpy as np
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from mlflow.models import infer_signature

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
    """Extends Simulator with clustering."""
    def generate_raw_data(self):
        """Generate balanced raw dataframe for clustering."""
        data = []
        for std in [3, 10, 20]:
            for _ in range(10):
                length = np.random.randint(50, 200)
                signal = Signal(length, std)
                mean = np.mean(signal.data)
                var = np.var(signal.data)
                data.append({'mean': mean, 'var': var})
        np.random.shuffle(data)
        return pd.DataFrame(data)

    def apply_clustering(self, df, n_clusters=3):
        """Apply KMeans clustering and evaluate."""
        features = df[['mean', 'var']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['cluster'] = kmeans.fit_predict(features)
        silhouette = silhouette_score(features, df['cluster'])
        # Log to MLflow
        with mlflow.start_run():
            mlflow.log_param("n_clusters", n_clusters)
            mlflow.log_metric("silhouette_score", silhouette)
            # Infer signature and provide input example
            signature = infer_signature(features, df['cluster'])
            mlflow.sklearn.log_model(
                sk_model=kmeans,
                name="kmeans_model",  # Use 'name' to avoid deprecation
                signature=signature,
                input_example=features.iloc[:1]
            )
        return df, silhouette

    def visualize_clusters(self, df):
        """Visualize clusters with Matplotlib/Seaborn."""
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x='mean', y='var', hue='cluster', data=df, palette='viridis')
        plt.title('Signal Clusters by Mean and Variance')
        plt.savefig('clusters.png')
        plt.close()

    def brainstorm_applications(self):
        """Brainstorm grouped insights."""
        ideas = [
            "Group signals for targeted analysis: e.g., optimize low-variance groups for stability.",
            "Use clusters to segment simulations: e.g., apply different difficulty levels per cluster.",
            "Detect anomalies: Clusters could highlight unusual patterns for further investigation."
        ]
        return ideas

def main():
    sim = MLSimulator()
    df = sim.generate_raw_data()
    clustered_df, score = sim.apply_clustering(df)
    print("Silhouette Score:", score)
    sim.visualize_clusters(clustered_df)
    print("Clusters saved to 'clusters.png'")
    ideas = sim.brainstorm_applications()
    print("Brainstormed Applications:")
    for idea in ideas:
        print("- " + idea)

if __name__ == "__main__":
    main()