# Import necessary libraries
import os
import sounddevice as sd
import numpy as np
import time
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

# Load environment variables from .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# --- New, Robust Device Selection ---
print("Available audio devices:")
devices = sd.query_devices()
input_devices = [] # This will store tuples of (index, name)

for i, device in enumerate(devices):
    # Only show input devices
    if device['max_input_channels'] > 0:
        print(f"  {i}: {device['name']}")
        input_devices.append((i, device['name'])) # Store the valid index and name

if not input_devices:
    print("No input devices found!")
    exit(1)

# Auto-select the best microphone device
preferred_devices = [2, 10, 1, 9, 8]  # Headset microphones first, then others
MICROPHONE_DEVICE = None

for device_id in preferred_devices:
    if device_id < len(devices) and devices[device_id]['max_input_channels'] > 0:
        MICROPHONE_DEVICE = device_id
        print(f"Auto-selected device {device_id}: {devices[device_id]['name']}")
        break

if MICROPHONE_DEVICE is None:
    # Fallback to first available input device
    MICROPHONE_DEVICE = input_devices[0][0]
    print(f"Fallback to device {MICROPHONE_DEVICE}: {devices[MICROPHONE_DEVICE]['name']}")

print(f"Using device {MICROPHONE_DEVICE}: {devices[MICROPHONE_DEVICE]['name']}\n")


# Global variable to signal the mic stream to stop
mic_stream_active = True

def main():
    global mic_stream_active
    try:
        # 1. Initialize the Deepgram Client
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(DEEPGRAM_API_KEY, config)

        # 2. Create a LiveTranscriptionClient
        dg_connection = deepgram.listen.live.v("1")

        # 3. Define event handlers
        def on_open(self, open, **kwargs):
            print("Connected to Deepgram")

        def on_message(self, result, **kwargs):
            transcript = result.channel.alternatives[0].transcript
            if len(transcript) > 0:
                print(f"Transcript: {transcript}")

        def on_error(self, error, **kwargs):
            print(f"Error: {error}")

        def on_close(self, close, **kwargs):
            print("\nConnection closed")
            global mic_stream_active
            mic_stream_active = False # Signal mic to stop

        # 4. Register the event handlers
        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        # 5. Define options and start the connection
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

        # 6. Define the audio callback (with Volume Test)
        def audio_callback(indata, frames, time, status):
            if status:
                print("Audio status:", status)
            
            # --- DEBUGGING STEP: Check audio volume ---
            volume_norm = np.linalg.norm(indata)
            print(f"Volume: {volume_norm:.2f}", end="\r") # Use carriage return
            # --- END DEBUGGING STEP ---
            
            if mic_stream_active:
                dg_connection.send(indata.tobytes())

        # 7. Start the microphone stream
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

        # 8. Finish the Deepgram connection
        dg_connection.finish()
        print("Finished.")

    except KeyboardInterrupt:
        print("\nStopping stream...")
        mic_stream_active = False
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()