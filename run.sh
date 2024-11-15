#!/bin/bash
LANGUAGE_PARAM=""
if [ ! -z "$WHISPER_LANGUAGE" ]; then
    LANGUAGE_PARAM="--language ${WHISPER_LANGUAGE}"
fi

PROMPT_PARAM=""
if [ ! -z "$PROMPT" ]; then
    PROMPT_PARAM="--prompt ${PROMPT}"
fi

DEBUG_PARAM=""
if [ ! -z "$DEBUG_AUDIO_PATH" ]; then
    DEBUG_PARAM="--debug-audio ${DEBUG_AUDIO_PATH}"
fi


python3 -m wyoming_whisper_openai --uri tcp://0.0.0.0:7891 --debug --openai-api-key "${OPENAI_API_KEY}" ${LANGUAGE_PARAM} ${PROMPT_PARAM} ${DEBUG_PARAM} "$@"
