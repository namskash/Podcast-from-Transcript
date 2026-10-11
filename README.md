# Podcast From Transcript

Generate podcast audio from transcript files with Gemini TTS.

This project is transcript-source agnostic. A transcript can come from any folder, repository, or generation workflow. The tool reads a transcript file, sends the text to Gemini TTS, and writes audio files to an output directory.

## Goals

- Convert transcript files to podcast audio.
- Support configurable Gemini TTS settings.
- Keep input and output paths configurable.
- Make each run reproducible.
- Keep secrets out of source code.

## Non-Goals

- This project does not manage transcript creation.
- This project does not require transcripts to live in this repository.
- This project does not commit generated audio files by default.

## Expected Workflow

1. Provide a transcript file path.
2. Select an output directory.
3. Configure Gemini TTS settings.
4. Run the generation script.
5. Review the generated audio files.

Example command shape:

```bash
python generate_podcast.py \
  --input /path/to/transcript.md \
  --output-dir outputs \
  --voice default
```

The exact command can change as the implementation develops.

## Configuration

Use environment variables for API credentials.

Example:

```bash
export GEMINI_API_KEY="your-api-key"
```

Do not hardcode API keys in source files, config files, or scripts.

Common configuration values:

- Transcript input path
- Output directory
- Gemini model name
- Voice name
- Audio format
- Chunk size
- Retry settings

## Output Structure

Recommended output paths:

```text
outputs/
  transcript-name/
    chunk-001.mp3
    chunk-002.mp3
    final.mp3
    metadata.json
```

Use stable names for chunk files. This makes retries and debugging easier.

## Safety

- Do not overwrite existing audio files without confirmation.
- Do not store secrets in git.
- Do not commit generated audio unless required.
- Log the input path, output path, and model settings for each run.

## Development Notes

Keep the code small and clear.

Preferred design:

- One command-line entry point
- Configurable input and output paths
- Clear validation before TTS calls
- Useful error messages
- Repeatable output names
- Optional chunking for long transcripts

## License

No license is defined yet.
