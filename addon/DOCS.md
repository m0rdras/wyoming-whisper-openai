# Home Assistant Add-on: OpenAI Whisper STT

## Installation

1. Click the Home Assistant My button below to open the add-on on your Home Assistant instance.
2. Click "Install".
3. Configure your OpenAI API key.
4. Start the add-on.

## Configuration

### Option: `openai_api_key` (required)

The API key for OpenAI's services. You can get one at https://platform.openai.com/api-keys

### Option: `language` (optional)

Language code for Whisper transcription (e.g., en, fr, de). Default is "en".

## How to use

Add this to your Home Assistant configuration:

```yaml
assist_pipeline:
  pipeline:
    name: OpenAIWhisperPipeline
  stt:
    engine: wyoming
host: localhost
port: 7891
```

