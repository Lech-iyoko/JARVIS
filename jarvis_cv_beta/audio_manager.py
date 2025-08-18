# Handles audio input/output for JARVIS CV Beta
import os
from dotenv import load_dotenv
from deepgram import PrerecordedOptions, DeepgramClient

# Load environment variable
load_dotenv()

# Path to audio file
AUDIO_FILE = "test_audio.wav" 
