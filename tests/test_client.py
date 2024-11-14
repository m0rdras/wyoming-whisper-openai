#!/usr/bin/env python3
import asyncio
import wave
from pathlib import Path
import sys

from wyoming.audio import AudioChunk, AudioStop
from wyoming.asr import Transcribe, Transcript
from wyoming.client import AsyncTcpClient

async def main():
    if len(sys.argv) != 2:
        print("Usage: poetry run python tests/test_client.py input.wav")
        sys.exit(1)

    wav_path = Path(sys.argv[1])
    
    print(f"Connecting to Wyoming server at localhost:7891...")
    async with AsyncTcpClient('localhost', 7891) as client:
        with wave.open(str(wav_path), 'rb') as wav_file:
            print(f"Sending audio file: {wav_path}")
            print(f"Format: {wav_file.getframerate()}Hz, {wav_file.getsampwidth()*8}bit, {wav_file.getnchannels()} channels")
            
            await client.write_event(Transcribe().event())

            chunk_size = 1024
            while True:
                audio_data = wav_file.readframes(chunk_size)
                if not audio_data:
                    break
                
                await client.write_event(
                    AudioChunk(
                        audio=audio_data,
                        rate=wav_file.getframerate(),
                        width=wav_file.getsampwidth(),
                        channels=wav_file.getnchannels(),
                    ).event()
                )

            print("Finished sending audio, waiting for transcription...")
            await client.write_event(AudioStop().event())

            # Wait for response
            while True:
                event = await client.read_event()
                if event is None:
                    break
                if Transcript.is_type(event.type):
                    transcript = Transcript.from_event(event)
                    print("Transcription:", transcript.text)
                    break

if __name__ == "__main__":
    asyncio.run(main()) 