import os
import time
import random
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Path to the music folder
MUSIC_FOLDER = "music"

# Load all music files from the folder
music_files = [file for file in os.listdir(MUSIC_FOLDER) if file.endswith(('.mp3', '.wav', '.ogg'))]

if not music_files:
    print("No music files found in the 'music' folder.")
    exit()

def play_random_song():
    """Load and play a random song from the music folder."""
    song = random.choice(music_files)
    pygame.mixer.music.load(os.path.join(MUSIC_FOLDER, song))
    pygame.mixer.music.play()
    print(f"Playing: {song}")

def main():
    play_random_song()
    playing = True  # Keep track of whether music is currently playing

    while True:
        time.sleep(60)  # Wait for 1 minute

        action = random.randint(0, 2)  # Randomly pick 0, 1, or 2
        if action == 0:
            print("Action: Do nothing")
            continue  # Do nothing and continue to the next iteration

        elif action == 1:
            if not playing:
                pygame.mixer.music.unpause()
                playing = True
                print("Action: Unpause music")

        elif action == 2:
            if playing:
                pygame.mixer.music.pause()
                playing = False
                print("Action: Pause music")

        # If the music has stopped naturally, load and play another random song
        if not pygame.mixer.music.get_busy() and playing:
            play_random_song()

if __name__ == "__main__":
    main()
