import pygame
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
from matplotlib import cm

data_path = "/Users/cemerturkan/Desktop/personal_projects/data/output_embed/"
metadata_df = pd.read_csv(data_path + 'embeddings_metadata.csv', index_col=0)
embeddings = np.load(data_path + 'embeddings.npy')

# Get labels from metadata
labels = metadata_df['label'].values  # Replace 'label' with the actual column name for labels

# Apply PCA
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

# Normalize the data with a margin
margin = 50  # Margin to avoid points at the edges
embeddings_2d = (embeddings_2d - embeddings_2d.min(axis=0)) / (embeddings_2d.max(axis=0) - embeddings_2d.min(axis=0))
embeddings_2d = embeddings_2d * (800 - 2 * margin) + margin

# Assign unique colors to labels
unique_labels = np.unique(labels)
label_to_color = {label: cm.tab20(i / len(unique_labels))[:3] for i, label in enumerate(unique_labels)}  # Use matplotlib's colormap
label_to_color = {label: tuple(int(c * 255) for c in rgb) for label, rgb in label_to_color.items()}  # Convert to 0-255 RGB

# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Interactive 2D PCA Visualization with Labels")
clock = pygame.time.Clock()

# Colors
WHITE = (0, 0, 0)
GREEN = (0, 255, 0)

# Initialize user-controlled point
user_point = np.array([400, 400])  # Start at the center of the screen

# Function to find the closest point
def find_closest_point(point, points):
    distances = np.linalg.norm(points - point, axis=1)
    return np.argmin(distances)

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle keyboard inputs for arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: user_point[0] -= 2
    if keys[pygame.K_RIGHT]: user_point[0] += 2
    if keys[pygame.K_UP]: user_point[1] -= 2
    if keys[pygame.K_DOWN]: user_point[1] += 2

    # Ensure the user-controlled point stays within bounds
    user_point[0] = np.clip(user_point[0], 0, 800)
    user_point[1] = np.clip(user_point[1], 0, 800)

    # Find the closest point in the embeddings
    closest_idx = find_closest_point(user_point, embeddings_2d)
    closest_point = embeddings_2d[closest_idx]

    # Draw all points
    for idx, (point, label) in enumerate(zip(embeddings_2d, labels)):
        color = label_to_color[label]
        size = 5 if idx != closest_idx else 10  # Highlight closest point by increasing size
        pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), size)

    # Draw the user-controlled point
    pygame.draw.circle(screen, GREEN, (int(user_point[0]), int(user_point[1])), 8)

    # Display updates
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
