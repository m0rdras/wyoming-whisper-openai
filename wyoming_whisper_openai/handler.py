"""Event handler for clients of the server."""
import argparse
import httpx
import logging
import wave

from io import BytesIO

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
            async with httpx.AsyncClient() as client:
                with BytesIO() as tmpfile:
                    with wave.open(tmpfile, 'wb') as wavfile:
                        wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
                        wavfile.writeframes(self.audio)

                        headers = {
                            "Authorization": f"Bearer {self.cli_args.openai_api_key}"
                        }
                        files = {
                            "file": ("audio.wav", tmpfile.getvalue(), "audio/wav")
                        }
                        data = {
                            "model": "whisper-1",
                            "response_format": "json"
                        }
                        if self.cli_args.language:
                            data["language"] = self.cli_args.language
                        
                        r = await client.post(
                            "https://api.openai.com/v1/audio/transcriptions",
                            headers=headers,
                            files=files,
                            data=data,
                            timeout=120.0
                        )
                        text = r.json()['text']

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self.audio = bytes()

            return False

        if Transcribe.is_type(event.type):
            _LOGGER.debug("Transcibe event")
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
