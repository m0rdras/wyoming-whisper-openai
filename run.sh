#!/bin/bash

# Initialize the args array with base arguments
args=(
    "-m" "wyoming_whisper_openai"
    "--uri" "tcp://0.0.0.0:7891"
    "--debug"
    "--openai-api-key" "${OPENAI_API_KEY}"
)

# Add language parameter if set
if [ -n "$WHISPER_LANGUAGE" ]; then
    args+=(--language "${WHISPER_LANGUAGE}")
fi

# Add prompt parameter if set
if [ -n "$PROMPT" ]; then
    args+=(--prompt "${PROMPT}")
fi

# Add debug parameter if set
if [ -n "$DEBUG_AUDIO_PATH" ]; then
    args+=(--debug-audio "${DEBUG_AUDIO_PATH}")
fi

# Add any additional arguments passed to the script
args+=("$@")

# Execute with all arguments
python3 "${args[@]}"
