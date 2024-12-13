import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Create 8 channels
channels = [pygame.mixer.Channel(i) for i in range(8)]

# List of audio files for the channels (replace these with your actual file paths)
audio_files = [
    "audio1.wav",
    "audio2.wav",
    "audio3.wav",
    "audio4.wav",
    "audio5.wav",
    "audio6.wav",
    "audio7.wav",
    "audio8.wav",
]

# Load the audio files into pygame.mixer.Sound objects
sounds = [pygame.mixer.Sound(file) for file in audio_files]

# Function to play sounds in order on their respective channels
def play_sounds_in_order():
    for i, sound in enumerate(sounds):
        print(f"Playing sound {i + 1} on channel {i}...")
        channels[i].play(sound)
        while channels[i].get_busy():  # Wait until the current sound finishes
            time.sleep(0.1)

# Run the function to play the sounds
try:
    play_sounds_in_order()
finally:
    # Quit the mixer when done
    pygame.mixer.quit()
