import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Load data
data_path = "/Users/cemerturkan/Desktop/personal_projects/data/output_embed/"
metadata_df = pd.read_csv(data_path + 'embeddings_metadata.csv', index_col=0)
embeddings = np.load(data_path + 'embeddings.npy')

# Apply PCA
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

# Add PCA components to metadata
metadata_df['PCA1'] = embeddings_2d[:, 0]
metadata_df['PCA2'] = embeddings_2d[:, 1]

# Visualization
plt.figure(figsize=(10, 8))
scatter = plt.scatter(metadata_df['PCA1'], metadata_df['PCA2'], c=metadata_df['label'], cmap='viridis', alpha=0.7)

# Add a legend for labels if metadata contains labels
if 'label' in metadata_df.columns:
    handles, labels = scatter.legend_elements()
    plt.legend(handles, metadata_df['label'].unique(), title="Labels")

plt.title("2D PCA Visualization of Embeddings")
plt.xlabel("PCA1")
plt.ylabel("PCA2")
plt.grid(alpha=0.3)
plt.show()
