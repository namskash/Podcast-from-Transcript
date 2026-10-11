from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash-tts"
DEFAULT_VOICE = "Ludo"
DEFAULT_SECOND_VOICE = "Tari"
SPEAKER_LINE_RE = re.compile(r"^\s*([A-Za-z][\w .'-]{0,48})\s*:\s*(.+?)\s*$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
PAUSE_RE = re.compile(r"^\s*\[\s*pause\s+(\d+)\s*seconds?\s*\]\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Turn:
    speaker: str | None
    text: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate podcast audio from a transcript file using Gemini TTS."
    )
    parser.add_argument("--input", "-i", required=True, help="Transcript file path")
    parser.add_argument("--output-dir", "-o", default="outputs", help="Output directory")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY", help="Env var holding Gemini API key")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini TTS model")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Default/prebuilt voice name")
    parser.add_argument("--second-speaker", dest="second_voice", default=DEFAULT_SECOND_VOICE, help="Default voice for a second detected speaker")
    parser.add_argument(
        "--speaker",
        action="append",
        default=[],
        metavar="NAME=VOICE",
        help="Speaker voice mapping; repeat for multi-speaker transcripts, e.g. --speaker Host=Puck",
    )
    parser.add_argument("--style", default="natural podcast narration", help="Speaking style")
    parser.add_argument("--chunk-chars", type=int, default=6000, help="Approx max chars per chunk")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite an existing output folder")
    return parser.parse_args(argv)


def require_file(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"Transcript not found: {path}")
    if not path.is_file():
        raise SystemExit(f"Transcript path is not a file: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"Transcript is empty: {path}")
    return text


def parse_speakers(values: Iterable[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --speaker value {value!r}; expected NAME=VOICE")
        name, voice = [part.strip() for part in value.split("=", 1)]
        if not name or not voice:
            raise SystemExit(f"Invalid --speaker value {value!r}; expected NAME=VOICE")
        mapping[name] = voice
    return mapping


def clean_transcript(text: str) -> str:
    return HTML_COMMENT_RE.sub("", text)


def transcript_to_turns(text: str) -> list[Turn]:
    text = clean_transcript(text)
    turns: list[Turn] = []
    buffer: list[str] = []
    current_speaker: str | None = None

    def flush() -> None:
        nonlocal buffer, current_speaker
        joined = "\n".join(line.strip() for line in buffer if line.strip()).strip()
        if joined:
            turns.append(Turn(current_speaker, joined))
        buffer = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if buffer:
                buffer.append("")
            continue
        if HEADING_RE.match(line):
            continue
        pause_match = PAUSE_RE.match(line)
        if pause_match:
            flush()
            turns.append(Turn(None, f"<pause {pause_match.group(1)} seconds>"))
            current_speaker = None
            continue
        match = SPEAKER_LINE_RE.match(line)
        if match:
            flush()
            current_speaker = match.group(1).strip()
            buffer.append(match.group(2).strip())
        else:
            buffer.append(line)
    flush()

    return turns or [Turn(None, text)]


def chunk_turns(turns: list[Turn], max_chars: int) -> list[list[Turn]]:
    if max_chars < 500:
        raise SystemExit("--chunk-chars must be at least 500")
    chunks: list[list[Turn]] = []
    current: list[Turn] = []
    current_len = 0

    for turn in turns:
        turn_len = len(turn.text) + (len(turn.speaker or "") + 2)
        if current and current_len + turn_len > max_chars:
            chunks.append(current)
            current = []
            current_len = 0
        current.append(turn)
        current_len += turn_len
    if current:
        chunks.append(current)
    return chunks


def single_speaker_config(voice: str) -> types.SpeechConfig:
    return types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
        )
    )


def multi_speaker_config(speaker_voices: dict[str, str], fallback_voice: str) -> types.SpeechConfig:
    configs = [
        types.SpeakerVoiceConfig(
            speaker=speaker,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            ),
        )
        for speaker, voice in speaker_voices.items()
    ]
    if len(configs) == 1:
        return single_speaker_config(next(iter(speaker_voices.values())))
    if not configs:
        return single_speaker_config(fallback_voice)
    return types.SpeechConfig(
        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(speaker_voice_configs=configs)
    )


def render_turn(turn: Turn, multi_speaker: bool) -> str:
    if turn.text.startswith("<pause "):
        return turn.text
    if multi_speaker:
        return f"{turn.speaker or 'Narrator'}: {turn.text}"
    return turn.text


def render_chunk_text(turns: list[Turn], style: str, multi_speaker: bool) -> str:
    body = "\n".join(render_turn(turn, multi_speaker) for turn in turns)
    instruction = (
        "Read this as a polished podcast conversation. "
        if multi_speaker
        else "Read this as polished podcast audio. "
    )
    return (
        f"{instruction}Style: {style}. "
        "Do not read speaker labels, headings, Markdown, HTML comments, or pause tags aloud. "
        "For tags like <pause 3 seconds>, insert that amount of silence.\n\n"
        f"{body}"
    )


def build_multi_speaker_contents(turns: list[Turn], style: str) -> list[types.Content]:
    parts: list[types.Part] = []
    last_speaker: str | None = None
    for turn in turns:
        speaker = turn.speaker or last_speaker
        if not speaker:
            continue
        last_speaker = speaker
        parts.append(
            types.Part(
                text=turn.text,
                speech_metadata=types.SpeechMetadata(speaker=speaker, style=style),
            )
        )
    return [types.Content(role="user", parts=parts)]


def generate_audio(client: genai.Client, model: str, contents: str | list[types.Content], speech_config: types.SpeechConfig) -> bytes:
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config,
        ),
    )
    try:
        data = response.candidates[0].content.parts[0].inline_data.data
    except (AttributeError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Gemini returned no audio data: {response!r}") from exc
    if not data:
        raise RuntimeError("Gemini returned empty audio data")
    return data


def safe_output_dir(base: Path, transcript: Path, overwrite: bool) -> Path:
    out_dir = base / transcript.stem
    if out_dir.exists() and not overwrite:
        raise SystemExit(f"Output directory already exists: {out_dir}\nUse --overwrite to replace files.")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).expanduser().resolve()
    output_base = Path(args.output_dir).expanduser().resolve()
    print(f"Loading transcript: {input_path}", flush=True)
    transcript = require_file(input_path)
    print(f"Loaded {len(transcript):,} characters", flush=True)
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key env var: {args.api_key_env}")

    speaker_voices = parse_speakers(args.speaker)
    turns = transcript_to_turns(transcript)
    used_speakers = sorted({turn.speaker for turn in turns if turn.speaker})
    missing = [speaker for speaker in used_speakers if speaker not in speaker_voices]
    for index, speaker in enumerate(missing):
        speaker_voices[speaker] = args.voice if index == 0 else args.second_voice

    chunks = chunk_turns(turns, args.chunk_chars)
    print(f"Detected {len(turns)} transcript turn(s)", flush=True)
    print(f"Prepared {len(chunks)} chunk(s)", flush=True)
    print(f"Using model: {args.model}", flush=True)
    print(f"Using default voice: {args.voice}", flush=True)
    print(f"Using default second voice: {args.second_voice}", flush=True)
    if speaker_voices:
        print(f"Speaker voices: {speaker_voices}", flush=True)
    out_dir = safe_output_dir(output_base, input_path, args.overwrite)
    print(f"Output directory: {out_dir}", flush=True)
    client = genai.Client(api_key=api_key)
    speech_config = multi_speaker_config(speaker_voices, args.voice)
    multi_speaker = len(speaker_voices) > 1

    audio_paths: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_text = render_chunk_text(chunk, args.style, multi_speaker)
        contents = build_multi_speaker_contents(chunk, args.style) if multi_speaker else chunk_text
        print(f"Generating chunk {index}/{len(chunks)} ({len(chunk_text):,} characters)...", flush=True)
        audio = generate_audio(client, args.model, contents, speech_config)
        audio_path = out_dir / f"chunk-{index:03d}.wav"
        audio_path.write_bytes(audio)
        audio_paths.append(str(audio_path))
        print(f"Wrote {audio_path} ({len(audio):,} bytes)", flush=True)
        time.sleep(0.2)

    metadata = {
        "input": str(input_path),
        "output_dir": str(out_dir),
        "model": args.model,
        "voice": args.voice,
        "speaker_voices": speaker_voices,
        "second_voice": args.second_voice,
        "style": args.style,
        "chunk_chars": args.chunk_chars,
        "chunks": audio_paths,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir / 'metadata.json'}", flush=True)
    print("Done", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        raise SystemExit(130)
