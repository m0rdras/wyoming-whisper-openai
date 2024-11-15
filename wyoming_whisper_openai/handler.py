"""Event handler for clients of the server."""
import argparse
import logging
import wave
import time
from pathlib import Path
from io import BytesIO

from openai import AsyncOpenAI
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

_LOGGER = logging.getLogger(__name__)

class WhisperAPIEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
            self,
            wyoming_info: Info,
            cli_args: argparse.Namespace,
            *args,
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.audio = bytes()
        self.audio_converter = AudioChunkConverter(
            rate=16000,
            width=2,
            channels=1,
        )

        # Verify API key is provided
        if not hasattr(cli_args, 'openai_api_key') or not cli_args.openai_api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=cli_args.openai_api_key)

        if hasattr(cli_args, 'debug_audio') and cli_args.debug_audio:
            self.debug_dir = Path(cli_args.debug_audio)
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            _LOGGER.info(f"Debug audio will be saved to {self.debug_dir}")
        else:
            self.debug_dir = None

        self.prompt = getattr(cli_args, 'prompt', None)

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            if not self.audio:
                _LOGGER.debug("Receiving audio")

            chunk = AudioChunk.from_event(event)
            chunk = self.audio_converter.convert(chunk)
            self.audio += chunk.audio

            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped")

            with BytesIO() as tmpfile:
                with wave.open(tmpfile, 'wb') as wavfile:
                    wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
                    wavfile.writeframes(self.audio)

                    if self.debug_dir:
                        timestamp = time.strftime("%Y%m%d-%H%M%S")
                        file_path = self.debug_dir / f"debug_audio_{timestamp}.wav"
                        file_path.write_bytes(tmpfile.getvalue())
                        _LOGGER.info(f"Saved debug audio to {file_path}")

                    # Reset position to start of file
                    tmpfile.seek(0)

                    params = {
                        "model": "whisper-1",
                        "response_format": "text",
                        "file": ("audio.wav", tmpfile, "audio/wav")
                    }

                    if self.cli_args.language:
                        params["language"] = self.cli_args.language

                    if self.prompt:
                        params["prompt"] = self.prompt

                    response = await self.client.audio.transcriptions.create(**params)
                    text = response

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self.audio = bytes()

            return False

        if Transcribe.is_type(event.type):
            _LOGGER.debug("Transcribe event")
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
