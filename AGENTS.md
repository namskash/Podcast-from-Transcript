# Podcast From Transcript Agent Guide

## Project Purpose

This repo contains code for generating podcast-style audio from transcript files using Gemini TTS.

The project should be transcript-source agnostic: transcripts may come from any directory, repo, or generated workflow. Do not assume a fixed source path.

## Expected Workflow

1. For audio generation, accept a transcript file path as input.
2. Read and validate the transcript.
3. Send transcript content to Gemini TTS.
4. Save ordered WAV chunks and `metadata.json` to a clear output path.
5. Log the transcript input path, model/config used, and generated audio path.

## Transcript Skill Scope

- Invoke `.agents/skills/podcast-transcript-builder/SKILL.md` only when creating a new transcript.
- Do not invoke it when reading, validating, converting, or generating audio from an existing transcript.
- For validation only, use `/validate-transcript <path-to-transcript-md>` or the validator directly; it must not modify the transcript.

## Configuration

- Use environment variables for secrets and API keys.
- Never hardcode Gemini/API credentials.
- Prefer CLI args or config files for:
  - transcript input path
  - output directory
  - voice/model settings
  - audio format
  - chunking behavior

## Safety Rules

- Never commit, push, or run git operations unless explicitly asked.
- Ask before overwriting existing generated audio.
- Keep generated audio files out of git unless explicitly requested.
- Avoid destructive cleanup commands without confirmation.

## Code Conventions

- Prefer small, focused scripts over large frameworks.
- Keep paths configurable; avoid repo-specific absolute paths.
- Make commands reproducible and easy to copy/paste.
- Add clear error messages for missing env vars, missing files, or failed TTS calls.
- If transcript length requires chunking, preserve ordering in output filenames.

## Outputs

Generated audio uses descriptive paths, for example:

- `outputs/<transcript-name>/chunk-001.wav`
- `outputs/<transcript-name>/metadata.json`

Do not overwrite existing generated audio without confirmation.
