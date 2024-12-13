import pygame
import time
import os
import random

pygame.mixer.init()

channels = [pygame.mixer.Channel(i) for i in range(8)]

audio_dir = "/Users/cemerturkan/Music/Logic/Bounces/exhibition/d"
counter = 0
audio_files = []
for f_name in os.listdir(audio_dir):
    if f_name.endswith('.mp3') and (counter < 8):
        path_to_file = audio_dir + '/' + f_name
        audio_files.append(path_to_file)
        counter += 1
    elif counter >= 8:
        break

sounds = [pygame.mixer.Sound(file) for file in audio_files]

def play_two_random_sounds():
    if len(sounds) < 2:
        print("Not enough sounds to play.")
        return

    random_indices = random.sample(range(len(sounds)), 2)
    sound1, sound2 = sounds[random_indices[0]], sounds[random_indices[1]]

    print(f"Playing sound {random_indices[0] + 1} and sound {random_indices[1] + 1} simultaneously...")
    channels[0].play(sound1)
    channels[1].play(sound2)

    while channels[0].get_busy() or channels[1].get_busy():
        time.sleep(0.1)

try:
    play_two_random_sounds()
finally:
    pygame.mixer.quit()
