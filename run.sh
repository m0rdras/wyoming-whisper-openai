#!/bin/bash
python3 -m wyoming_whisper_api_client --uri tcp://0.0.0.0:7891 --debug --openai-api-key "${OPENAI_API_KEY}" "$@"

