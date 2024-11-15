#!/bin/bash
LANGUAGE_PARAM=""
if [ ! -z "$WHISPER_LANGUAGE" ]; then
    LANGUAGE_PARAM="--language ${WHISPER_LANGUAGE}"
fi

python3 -m wyoming_whisper_openai --uri tcp://0.0.0.0:7891 --debug --openai-api-key "${OPENAI_API_KEY}" ${LANGUAGE_PARAM} "$@"

