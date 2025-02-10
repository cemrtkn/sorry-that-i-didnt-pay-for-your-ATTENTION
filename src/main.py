import pygame
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
from matplotlib import cm
import os
from gpiozero import MCP3008
from gpiozero.pins.rpigpio import RPiGPIOFactory  # Import RPi.GPIO pin factory
import math
import sys
import threading
from config import embed_dir, audio_dir

def timeout(channel):
    channel.stop()


def check_hdmi_connection():
    paths = [
        "/sys/class/drm/card1-HDMI-A-1/status",
        "/sys/class/drm/card0-HDMI-A-1/status"
    ]
    
    for path in paths:
        try:
            with open(path, "r") as file:
                status = file.read().strip()
                return (status=="connected")  # Returns 'connected' or 'disconnected'
        except FileNotFoundError:
            continue  # Try the next path if the file doesn't exist
    
    return False  # If no valid path is found

def calculate_position(up_down, right_left):
    # normalize the ratios
    ldr1_norm, ldr2_norm = up_down
    ldr3_norm, ldr4_norm = right_left
    
    # compute contributions to x and y
    y = ldr1_norm - ldr2_norm

    x = ldr4_norm - ldr3_norm
    
    # normalize the coordinates
    magnitude = max(abs(x), abs(y),1)
    x /= magnitude
    y /= magnitude

    
    return x,y

# Function to find the closest point
def find_closest_point(point, points):
    distances = np.linalg.norm(points - point, axis=1)
    return np.argmin(distances)
def main(visualize=False):
    data_path = embed_dir
    metadata_df = pd.read_csv(data_path + 'embeddings_metadata.csv', index_col=0)
    embeddings = np.load(data_path + 'embeddings.npy')

    # Get labels from metadata
    labels = metadata_df['label'].values

    # Apply PCA
    pca = PCA(n_components=2)
    pca_fit = pca.fit(embeddings)
    embeddings_2d = pca_fit.transform(embeddings)

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
    ldr3 = MCP3008(channel=2, pin_factory=factory)
    ldr4 = MCP3008(channel=3, pin_factory=factory)

    baseline1 = ldr1.value
    baseline2 = ldr2.value
    baseline3 = ldr3.value
    baseline4 = ldr4.value


    channels = [pygame.mixer.Channel(i) for i in range(1)]
    timer = threading.Timer(120, timeout, args=(channels[0],))

    audio_dir = audio_dir
    audio_files = []
    for f_name in list(metadata_df.index):
        f_name = f_name.split('_')[-1]
        audio_path =audio_dir + '/' +f_name + '.mp3'
        audio_files.append(audio_path)

    sounds = [pygame.mixer.Sound(file) for file in audio_files]
    if visualize:
        screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Interactive 2D PCA Visualization with Labels")
    clock = pygame.time.Clock()

    # Colors
    WHITE = (0, 0, 0)
    GREEN = (0, 255, 0)

    # Initialize user-controlled point
    user_point = np.array([400, 400])  # Start at the center of the screen

    prev_closest_idx = 51 # out of bounds
    running = True
    while running:           
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
         
        up_down = [(ldr1.value/baseline1),(ldr4.value/baseline4)]
        right_left = [(ldr2.value/baseline2),(ldr3.value/baseline3)]
        x,y = calculate_position(up_down, right_left)

        """print("Up-down")
        print(up_down)
        print(y)
        print("-"*40)

        print("Right-left")
        print(right_left)
        print(x)
        print("-"*40)"""

        
        user_point[0] = 400 + (400*x)
        user_point[1] = 400 + (400*y)


        # Ensure the user-controlled point stays within bounds
        user_point[0] = np.clip(user_point[0], 0, 800)
        user_point[1] = np.clip(user_point[1], 0, 800)

        # Find the closest point in the embeddings
        closest_idx = find_closest_point(user_point, embeddings_2d)
        closest_point = embeddings_2d[closest_idx]
        if closest_idx != prev_closest_idx:
            channels[0].stop()
            channels[0].play(sounds[closest_idx], loops=-1) #play in a loop
            if timer.is_alive():
                timer.cancel()
            timer = threading.Timer(120, timeout, args=(channels[0],))
            timer.start()

        # Draw all points
        if visualize:
            screen.fill(WHITE)
            for idx, (point, label) in enumerate(zip(embeddings_2d, labels)):
                color = label_to_color[label]
                size = 5 if idx != closest_idx else 10  # Highlight closest point by increasing size
                pygame.draw.circle(screen, color, (int(point[0]), int(point[1])), size)

            # Draw the user-controlled point
            pygame.draw.circle(screen, GREEN, (int(user_point[0]), int(user_point[1])), 8)
            pygame.display.flip()

        prev_closest_idx = closest_idx        
        clock.tick(30)

    pygame.quit()
    pygame.mixer.quit()


if __name__ == "__main__":
    visualize = sys.argv[1].lower() in ('true', '1', 't', 'y', 'yes')
    if check_hdmi_connection(): #display attached -> not in automatic script running mode
        print("script was not run because the user is here")
    else:
        main(visualize)
    
