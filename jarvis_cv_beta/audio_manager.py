# Import necessary libraries
import os
import sounddevice as sd
import numpy as np
import websockets
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DG_URL = "wss://api.deepgram.com/v1/listen?model=nova-3&smart_format=true"

# Print available devices and let user select
print("Available audio devices:")
devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:  # Only show input devices
        print(f"  {i}: {device['name']} ({device['hostapi']})")

# Select microphone device (you can change this number based on your output)
MICROPHONE_DEVICE = 7  # Headset Microphone (2- Wireless Controller), Windows DirectSound
print(f"Using device {MICROPHONE_DEVICE}: {devices[MICROPHONE_DEVICE]['name']}")

# Async queue to buffer audio chunks
audio_queue = asyncio.Queue()

# Callback function for InputStream
def audio_callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)
    # Convert float32 to int16 and put in queue
    audio_data = (indata * 32767).astype(np.int16)
    audio_queue.put_nowait(audio_data.copy())

# Main function to handle both streaming and receiving
async def main():
    try:
        async with websockets.connect(DG_URL, additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}) as ws:
            print("Connected to Deepgram")
            
            # Start audio stream with selected device
            with sd.InputStream(
                device=MICROPHONE_DEVICE,
                samplerate=16000, 
                channels=1, 
                dtype='float32', 
                callback=audio_callback,
                blocksize=1024
            ):
                print("Mic stream started")
                
                # Create tasks for sending audio and receiving transcripts
                async def send_audio():
                    while True:
                        try:
                            chunk = await asyncio.wait_for(audio_queue.get(), timeout=1.0)
                            await ws.send(chunk.tobytes())
                        except asyncio.TimeoutError:
                            # Send keepalive message if no audio for 1 second
                            await ws.send(json.dumps({"type": "KeepAlive"}))
                
                async def receive_transcripts():
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if 'channel' in data:
                                transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                                if transcript.strip():
                                    print("Transcript:", transcript)
                        except json.JSONDecodeError:
                            print("Received non-JSON message:", message)
                
                # Run both tasks concurrently
                await asyncio.gather(send_audio(), receive_transcripts())
                
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your microphone is working and the device number is correct.")

asyncio.run(main())