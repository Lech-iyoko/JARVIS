# Import necessary libraries
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# Load environment variables from .env file
load_dotenv()

# Define the path to your audio file
AUDIO_FILE = "test_audio.wav"

def main():
    """
    Main function to transcribe an audio file using Deepgram.
    """
    try:
        # STEP 1: Get your API key from the environment variable
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            print("Error: DEEPGRAM_API_KEY not found in .env file.")
            return

        # STEP 2: Initialize the Deepgram Client
        deepgram = DeepgramClient(api_key)

        # STEP 3: Open the audio file
        with open(AUDIO_FILE, 'rb') as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 4: Configure Deepgram options
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 5: Call the API with the audio file and options
        print("Sending request to Deepgram...")
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        
        # Print the transcription
        transcription = response.results.channels[0].alternatives[0].transcript
        print(f"\nTranscription: {transcription}\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()