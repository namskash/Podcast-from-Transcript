# Project Init Decisions

Date: 2026-10-11

- Used Python for the first project version.
- Added a CLI command: `podcast-from-transcript`.
- Used `google-genai` as the Gemini API client.
- Set the default TTS model to `gemini-3.8-flash-tts`.
- Set the default voice to `Kore`.
- Made the API key env var configurable with `--api-key-env`.
- Did not hardcode secrets.
- Made transcript input path configurable with `--input`.
- Made output directory configurable with `--output-dir`.
- Wrote generated audio as WAV chunk files.
- Used stable chunk names: `chunk-001.wav`, `chunk-002.wav`, and so on.
- Added `metadata.json` for each run.
- Logged input path, output path, model, voice, style, and chunk data.
- Added basic speaker parsing for lines like `Host: text`.
- Added speaker voice mapping with repeated `--speaker Name=Voice` options.
- Used the default voice for speakers that have no explicit mapping.
- Added chunking by character count with `--chunk-chars`.
- Stopped overwrite by default if the output folder already exists.
- Added `--overwrite` for explicit replacement.
- Updated `.gitignore` to keep generated outputs and local Python files out of git.
- Updated the README with install and run commands.
