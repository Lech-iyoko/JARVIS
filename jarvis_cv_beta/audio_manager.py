import os
import time
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    DeepgramWsClientOptions,
    DeepgramClientEnvironment,
    LiveTranscriptionEvents,
    LiveOptions
)

# Load environment variables from .env file
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Define environment (optional unless self-hosting)
env = DeepgramClientEnvironment(host="api.deepgram.com")

# --- Robust Device Selection ---
print("Available audio devices:")
devices = sd.query_devices()
input_devices = []

for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"  {i}: {device['name']}")
        input_devices.append((i, device['name']))

if not input_devices:
    print("No input devices found!")
    exit(1)

MICROPHONE_DEVICE = 9
print(f"Using device {MICROPHONE_DEVICE}: {devices[MICROPHONE_DEVICE]['name']}\n")

# Global variable to signal the mic stream to stop
mic_stream_active = True

def main():
    global mic_stream_active
    try:
        # ✅ FIX: Wrap ws_options inside DeepgramClientOptions
        ws_options = DeepgramWsClientOptions(
            options={
                "keepalive": "true"
            }
        )
        client_config = DeepgramClientOptions(
            environment=env,
            ws_options=ws_options
        )
        deepgram = DeepgramClient(DEEPGRAM_API_KEY, client_config)

        # Create a LiveTranscriptionClient
        dg_connection = deepgram.listen.websocket.v("1")

        # Event handlers
        def on_open(self, open, **kwargs):
            print("Connected to Deepgram (using new .websocket API)")

        def on_message(self, result, **kwargs):
            transcript = result.channel.alternatives[0].transcript
            if len(transcript) > 0:
                print(f"Transcript: {transcript}")

        def on_error(self, error, **kwargs):
            print(f"Error: {error}")

        def on_close(self, close, **kwargs):
            print("\nConnection closed")
            global mic_stream_active
            mic_stream_active = False

        # Register event handlers
        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        # Define transcription options
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            sample_rate=16000,
            encoding="linear16"
        )
        if not dg_connection.start(options):
            print("Failed to connect to Deepgram")
            return

        # Audio callback
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            volume_norm = np.linalg.norm(indata)
            print(f"Volume: {volume_norm:.2f}", end="\r")
            if mic_stream_active:
                dg_connection.send(indata.tobytes())

        # Start microphone stream
        print("Starting microphone stream... press Ctrl+C to stop.\n")
        with sd.InputStream(
            device=MICROPHONE_DEVICE,
            samplerate=16000,
            channels=1,
            dtype='int16',
            callback=audio_callback,
            blocksize=1024
        ):
            while mic_stream_active:
                time.sleep(0.1)

        # Finish connection
        dg_connection.finish()
        print("Finished.")

    except KeyboardInterrupt:
        print("\nStopping stream...")
        mic_stream_active = False
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
