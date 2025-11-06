# modules/voice_streamer.py
import os
import sounddevice as sd
import time
import queue
from dotenv import load_dotenv

from deepgram import DeepgramClient
from deepgram.core.events import EventType

class VoiceStreamer:
    def __init__(self, on_final_transcript):
        load_dotenv()
        DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
        if not DEEPGRAM_API_KEY:
            raise EnvironmentError("DEEPGRAM_API_KEY not found in .env file.")

        # --- THIS IS THE FIX (Part 1) ---
        # We no longer detect sample rate. We just get the device index.
        self.mic_device = self._select_microphone()
        self.sample_rate = 16000  # We will HARDCODE 16kHz
        # --- END OF FIX ---
        
        self.mic_stream_active = True
        self.on_final_transcript = on_final_transcript
        self.audio_queue = queue.Queue()

        self.deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.dg_connection = None
        print(f"✅ VoiceStreamer initialized (Forcing 16000 Hz).")
        

    def _select_microphone(self):
        """
        Presents a list of microphones and forces the user to select one.
        """
        print("Available audio devices:")
        devices = sd.query_devices()
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']}")
                input_devices.append((i, device['name']))
        if not input_devices:
            raise EnvironmentError("No input devices found!")

        while True:
            try:
                choice_str = input(f"\nPlease select your microphone's device number: ")
                choice_int = int(choice_str)
                
                if any(index == choice_int for index, name in input_devices):
                    print(f"Using device {choice_int}: {devices[choice_int]['name']}\n")
                    # Return only the index
                    return choice_int
                else:
                    print(f"Error: '{choice_int}' is not in the list.")
            except ValueError:
                print("Error: Please enter a valid number.")

    def _audio_callback(self, indata, frames, time, status):
        """
        This is the "Producer" - it runs on a high-priority audio thread.
        """
        if status:
            print(f"Audio status: {status}")
        if self.mic_stream_active:
            self.audio_queue.put(indata.tobytes())

    # --- Deepgram Event Handlers (v2 Style) ---
    def _register_event_handlers(self):
        """Registers all Deepgram event handlers using EventType."""
        self.dg_connection.on(EventType.OPEN, self._on_open)
        self.dg_connection.on(EventType.MESSAGE, self._on_message)
        self.dg_connection.on(EventType.ERROR, self._on_error)
        self.dg_connection.on(EventType.CLOSE, self._on_close)

    def _on_open(self, *args, **kwargs):
        print("✅ Connected to Deepgram (Listen v2)")
        self.dg_connection.start_listening()

    def _on_message(self, *args, result=None, **kwargs):
        """
This is called by Deepgram when a transcript is received.
        """
        if result is None:
            return
            
        transcript = result.channel.alternatives[0].transcript
        
        if not transcript.strip():
            return # Ignore empty transcripts

        if result.is_final:
            print(" " * 80, end="\r") # Clear the "Hearing" line
            self.on_final_transcript(transcript) # Call the callback
        else:
            # Print interim results
            print(f"Hearing: {transcript}...", end="\r")

    def _on_error(self, *args, error=None, **kwargs):
        print(f"❌ Deepgram Error: {error}")

    def _on_close(self, *args, **kwargs):
        print("\nConnection to Deepgram closed.")
        self.mic_stream_active = False

    def start_streaming(self):
        """
        Main streaming loop.
        """
        try:
            # --- THIS IS THE FIX (Part 2) ---
            # We tell Deepgram to EXPECT 16kHz
            with self.deepgram.listen.v2.connect(
                model="flux-general-en",
                encoding="linear16",
                sample_rate=self.sample_rate # This is 16000
            ) as connection:
            # --- END OF FIX ---
                
                self.dg_connection = connection
                self._register_event_handlers()
                
                print("Starting microphone stream... press Ctrl+C to stop.\n")
                
                # --- THIS IS THE FIX (Part 3) ---
                # We tell sounddevice to PROVIDE 16kHz
                # It will handle resampling internally.
                with sd.InputStream(
                    device=self.mic_device,
                    samplerate=self.sample_rate, # This is 16000
                    channels=1,
                    dtype='int16',
                    callback=self._audio_callback,
                    blocksize=1024
                ):
                # --- END OF FIX ---
                    
                    # This is the "Consumer" loop
                    while self.mic_stream_active:
                        try:
                            data = self.audio_queue.get(timeout=0.1)
                            self.dg_connection.send_media(data)
                        except queue.Empty:
                            pass 
        
        except KeyboardInterrupt:
            print("\nStopping stream...")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.mic_stream_active = False
            self.audio_queue.put(None)
            if self.dg_connection:
                pass 
            print("Stream finished.")

# --- Test Block ---
if __name__ == "__main__":
    def dummy_callback(transcript):
        print(f"--- TEST CALLBACK RECEIVED: {transcript} ---")
    
    try:
        streamer = VoiceStreamer(on_final_transcript=dummy_callback)
        streamer.start_streaming()
    except Exception as e:
        print(f"An error occurred: {e}")