#!/usr/bin/env python3
import argparse
import asyncio
import logging
from functools import partial
from pathlib import Path
from typing import Optional

from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import __version__
from .const import WHISPER_LANGUAGES
from .handler import WhisperAPIEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="unix:// or tcp://")
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    parser.add_argument("--debug-audio", default=None, help="Write audio to debug directory")
    parser.add_argument(
        "--log-format", default=logging.BASIC_FORMAT, help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print version and exit",
    )
    parser.add_argument(
        "--openai-api-key",
        required=True,
        help="OpenAI API key for Whisper transcription"
    )
    parser.add_argument(
        "--language",
        help="Language code for Whisper transcription (e.g., en, fr, de). Leave empty for auto-detection",
        choices=WHISPER_LANGUAGES + [""],
        default=""
    )
    parser.add_argument(
        "--prompt",
        help="Initial prompt for Whisper transcription (default: empty)",
        default=None
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="whisper-openai",
                description="OpenAI Whisper API Client",
                attribution=Attribution(
                    name="OpenAI",
                    url="https://openai.com/research/whisper"
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name="Whisper",
                        description="OpenAI Whisper API",
                        attribution=Attribution(
                            name="OpenAI",
                            url="https://platform.openai.com/docs/guides/speech-to-text"
                        ),
                        installed=True,
                        languages=WHISPER_LANGUAGES,
                        version="1.0",
                    )
                ],
            )
        ],
    )

    # Load converted whisper API

    server = AsyncServer.from_uri(args.uri)
    _LOGGER.info("Ready")
    model_lock = asyncio.Lock()
    await server.run(
        partial(
            WhisperAPIEventHandler,
            wyoming_info,
            args
        )
    )


# -----------------------------------------------------------------------------


def run() -> None:
    asyncio.run(main(), debug=True)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
