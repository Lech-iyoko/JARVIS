# main.py
from modules.voice_streamer import VoiceStreamer
from modules.llm_client import GroqClient
from modules.tts_client import ElevenLabsClient
import time

class Orchestrator:
    def __init__(self):
        print("Initializing clients...")
        self.groq_client = GroqClient()
        self.tts_client = ElevenLabsClient(voice_id="JBFqnCBsd6RMkjVDRZzb")
        
        # Pass this class's method as the callback
        self.voice_streamer = VoiceStreamer(
            on_final_transcript=self.handle_final_transcript
        )
        print("--- All clients initialized. ---")

    def handle_final_transcript(self, transcript):
        """
        This is the core logic loop!
        Called by VoiceStreamer when a final transcript is ready.
        """
        if not transcript.strip():
            print("Received empty transcript, ignoring.")
            return

        print(f"\n[User]: {transcript}")
        
        # 1. Send text to LLM
        print("Sending to Groq...")
        llm_response = self.groq_client.generate_response(transcript)
        
        print(f"[VISION]: {llm_response}")

        # 2. Send LLM response to TTS
        self.tts_client.speak_text_stream(llm_response)
        
        # 3. Add a small buffer to avoid immediate re-triggering
        print("\nListening...")
        time.sleep(0.5)

    def start(self):
        """
        Starts the main listening loop.
        """
        # This function blocks until streaming is stopped
        self.voice_streamer.start_streaming()

if __name__ == "__main__":
    print("--- Starting VISION Voice Loop ---")
    try:
        orchestrator = Orchestrator()
        orchestrator.start()
    except KeyboardInterrupt:
        print("\nOrchestrator stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
