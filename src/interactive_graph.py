import pygame
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
from matplotlib import cm
import os
from gpiozero import MCP3008
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Import RPi.GPIO pin factory


data_path = "/home/cemerturkan/Desktop/projects/find-my-music/data/output_embed/"
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
os.environ["SDL_AUDIODRIVER"] = "alsa"  # Use ALSA driver
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.set_num_channels(1)


# Set the pin factory to RPi.GPIO
factory = RPiGPIOFactory()
ldr1 = MCP3008(channel=0, pin_factory=factory)
ldr2 = MCP3008(channel=1, pin_factory=factory)
baseline1 = ldr1.value
baseline2 = ldr2.value

channels = [pygame.mixer.Channel(i) for i in range(1)]

audio_dir = "/home/cemerturkan/Desktop/projects/find-my-music/data/songs/"
audio_files = []
for f_name in list(metadata_df.index):
    f_name = f_name.split('_')[-1]
    audio_path =audio_dir + '/' +f_name + '.mp3'
    audio_files.append(audio_path)

sounds = [pygame.mixer.Sound(file) for file in audio_files]

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

prev_closest_idx = 38 # out of bounds
running = True
while running:
    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle keyboard inputs for arrow keys
    # get the max of up and down so we know what side we are at
    # ldr value is smaller the closer the light source is     
    up_down = [(ldr1.value/baseline1),(ldr2.value/baseline2)]

    y = min(up_down)
    y_side = up_down.index(y)
    y = round(y,2)
    if y_side == 1: #down
        y *= -1
        
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: user_point[0] -= 2
    if keys[pygame.K_RIGHT]: user_point[0] += 2
    print(up_down)
    print(400 + (400*y))
    user_point[1] = 400 + (400*y)
#     if keys[pygame.K_UP]: user_point[1] -= 2
#     if keys[pygame.K_DOWN]: user_point[1] += 2

    # Ensure the user-controlled point stays within bounds
    user_point[0] = np.clip(user_point[0], 0, 800)
    user_point[1] = np.clip(user_point[1], 0, 800)

    # Find the closest point in the embeddings
    closest_idx = find_closest_point(user_point, embeddings_2d)
    closest_point = embeddings_2d[closest_idx]

    if closest_idx != prev_closest_idx:
        channels[0].stop()
        channels[0].play(sounds[closest_idx])
    



    # Draw all points
    for idx, (point, label) in enumerate(zip(embeddings_2d, labels)):
        color = label_to_color[label]
        size = 5 if idx != closest_idx else 10  # Highlight closest point by increasing size
        pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), size)

    # Draw the user-controlled point
    pygame.draw.circle(screen, GREEN, (int(user_point[0]), int(user_point[1])), 8)

    prev_closest_idx = closest_idx
    # Display updates
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
pygame.mixer.quit()
