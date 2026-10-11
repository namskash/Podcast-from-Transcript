# Podcast From Transcript

Generate podcast-style audio from a transcript file using Gemini TTS.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
export GEMINI_API_KEY="AQ.s6aaA7ASHVB67akla97asd7hsd6a5_hAhAGoTchya" # Read that again ;)
```

## Basic usage

```bash
podcast-from-transcript \
  --input /path/to/transcript.md \
  --output-dir outputs
```

Output is written to:

```text
outputs/<transcript-name>/
  chunk-001.wav
  metadata.json
```

Long transcripts are split into ordered chunks:

```text
outputs/<transcript-name>/
  chunk-001.wav
  chunk-002.wav
  chunk-003.wav
  metadata.json
```

## Options

```bash
podcast-from-transcript \
  --input /path/to/transcript.md \
  --output-dir outputs \
  --model gemini-3.8-flash-tts \
  --voice Ludo \
  --second-speaker Tari \
  --style "natural podcast narration" \
  --chunk-chars 6000
```

- `--input`, `-i`: transcript file path
- `--output-dir`, `-o`: output folder, default `outputs`
- `--api-key-env`: API key environment variable, default `GEMINI_API_KEY`
- `--model`: Gemini TTS model
- `--voice`: default first voice
- `--second-speaker`: default second speaker voice
- `--style`: speaking style prompt
- `--chunk-chars`: approximate max characters per chunk
- `--overwrite`: replace an existing output folder

## Speaker voices

For speaker-labeled transcripts:

```text
Host: Welcome back.
Guest: Thanks for having me.
```

Map speakers to voices:

```bash
podcast-from-transcript \
  --input /path/to/transcript.md \
  --speaker Host=Ludo \
  --speaker Guest=Tari
```

Repeat `--speaker NAME=VOICE` for each speaker. Without explicit mappings, the first detected speaker uses `--voice` and the second uses `--second-speaker`.

## Metadata

Each run writes `metadata.json` with the input path, output path, model, voice settings, style, chunk size, and generated chunk files.

## Notes

- Existing output folders are not overwritten unless `--overwrite` is passed.
- Keep API keys in environment variables.
- Generated audio is ignored by git unless you intentionally add it.
