import os
import sounddevice as sd
from unreal_speech import UnrealSpeech
from dotenv import load_dotenv

class UnrealSpeechClient:
    def __init__(self, voice_id="Scarlett"):
        load_dotenv()
        api_key = os.getenv("UNREAL_SPEECH_API_KEY")
        if not api_key:
            raise EnvironmentError("UNREAL_SPEECH_API_KEY not found in .env file.")
        
        self.client = UnrealSpeech(api_key=api_key)
        self.voice_id = voice_id  # Scarlett is a good, fast voice
        print("UnrealSpeech Client initialized.")

    def speak_text(self, text_to_speak):
        """
        Generates audio from text and plays it back immediately.
        """
        try:
            # 1. Generate the audio stream
            # We use stream=True for the lowest latency
            audio_stream = self.client.stream(
                text_to_speak,
                voice_id=self.voice_id,
                bitrate="192k" # High quality audio
            )

            # 2. Get audio data and sample rate
            # .audio is a numpy array, .sample_rate is an int (e.g., 44100)
            audio_data = audio_stream.audio
            sample_rate = audio_stream.sample_rate

            # 3. Play the audio
            print(f"Playing audio: '{text_to_speak}'")
            sd.play(audio_data, sample_rate)
            sd.wait()  # Wait until the audio has finished playing
            print("Finished speaking.")

        except Exception as e:
            print(f"Error calling UnrealSpeech API or playing audio: {e}")

# --- Test Block ---
# This part will only run when you execute this file directly
if __name__ == "__main__":
    try:
        tts_client = UnrealSpeechClient()
        test_text = "Hello, this is a test of the text to speech system."
        
        tts_client.speak_text(test_text)
        
    except Exception as e:
        print(f"An error occurred during the test: {e}")