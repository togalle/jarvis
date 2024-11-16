#!/usr/bin/env python3
import speech_recognition as sr
import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from playsound import playsound
import re

# Set up Spotify API authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="1b6d9646695b4117af8d4cb6f3a723b6",
        client_secret="437399a5baf748ff97d6a6ac8794088a",
        redirect_uri="http://localhost:8888/callback",
        scope="user-modify-playback-state,user-read-playback-state",
    )
)

model = Model()

# Configure microphone settings
CHUNK = 80 * 60  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # 16kHz sample rate


def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10)  # Listen for 5 seconds
            command = recognizer.recognize_google(
                audio
            ).lower()  # Convert speech to text
            print(f"Command: {command}")
            return command
        except sr.UnknownValueError:
            print("Command not understood.")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
    return None


# Spotify control functions
def play_music():
    sp.start_playback()
    print("Playing music on Spotify.")


def pause_music():
    sp.pause_playback()
    print("Paused Spotify playback.")


def skip_track():
    sp.next_track()
    print("Skipped to the next track.")


def previous_track():
    sp.previous_track()
    print("Went back to the previous track.")


def increase_volume():
    # This will increase the volume by a predefined amount (e.g., 10%)
    current_volume = sp.current_playback()["device"]["volume_percent"]
    new_volume = min(current_volume + 10, 100)  # Don't exceed 100%
    sp.volume(new_volume)
    print(f"Increased volume to {new_volume}%.")


def decrease_volume():
    # This will decrease the volume by a predefined amount (e.g., 10%)
    current_volume = sp.current_playback()["device"]["volume_percent"]
    new_volume = max(current_volume - 10, 0)  # Don't go below 0%
    sp.volume(new_volume)
    print(f"Decreased volume to {new_volume}%.")


def set_volume_to(percentage):
    # Sets the volume to a specific percentage
    percentage = max(0, min(percentage, 100))  # Ensure it's between 0 and 100
    sp.volume(percentage)
    print(f"Set volume to {percentage}%.")


def execute_command(command):
    if any(word in command for word in ["start", "play", "resume"]):
        sp.start_playback()
        print("Playing music on Spotify.")
    elif any(word in command for word in ["pause", "stop"]):
        sp.pause_playback()
        print("Paused Spotify playback.")
    elif any(word in command for word in ["next", "skip", "forward"]):
        sp.next_track()
        print("Skipped to the next track.")
    elif any(word in command for word in ["previous", "back"]):
        sp.previous_track()
        print("Went back to the previous track.")
    elif any(word in command for word in ["increase volume", "higher volume"]):
        increase_volume()
    elif any(word in command for word in ["decrease volume", "lower volume"]):
        decrease_volume()
    elif re.search(r"(\d+)%", command):
        # If the command contains "set volume to X%"
        match = re.search(r"(\d+)%", command)
        volume_percentage = int(match.group(1))
        set_volume_to(volume_percentage)
    else:
        print(f"Command '{command}' not recognized.")


def main():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("Listening for 'Jarvis'...")

    last_command_time = time.time()

    try:
        while True:
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            frame = np.frombuffer(audio_data, dtype=np.int16)
            prediction = model.predict(frame)
            if prediction["hey_jarvis"] > 0.5:
                current_time = time.time()
                if current_time - last_command_time >= 2:
                    print("Jarvis is listening...")
                    playsound("jarvis.mp3")
                    command = recognize_command()
                    if command:
                        last_command_time = current_time
                        if command == "exit":
                            break
                        execute_command(command)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
