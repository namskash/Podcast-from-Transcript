#!/usr/bin/env python3
"""Validate the project's podcast transcript format."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SPEAKER_RE = re.compile(r"^([A-Za-z][\w .'-]{0,48}):\s+(.+)$")
PAUSE_RE = re.compile(r"^\[pause \d+ seconds\]$")
HUMOR_MARKER = "<!-- HUMOR -->"
QUOTED_SPEAKER_RE = re.compile(r'^"[^"\n]+":')


def validate(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return [f"file not found: {path}"]
    except UnicodeDecodeError as exc:
        return [f"file is not valid UTF-8: {exc}"]
    except OSError as exc:
        return [f"could not read file: {exc}"]

    nonempty = [(number, line) for number, line in enumerate(lines, 1) if line.strip()]
    if not nonempty:
        return ["transcript is empty"]

    first_number, first_line = nonempty[0]
    title_seen = first_line.startswith("# ") and bool(first_line[2:].strip())

    if title_seen:
        dialogue_started = False
    else:
        dialogue_started = True

    current_speaker: str | None = None

    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            current_speaker = None
            continue

        if title_seen and number == first_number:
            continue

        if stripped.startswith("#"):
            errors.append(f"line {number}: only one optional title is allowed, before dialogue")
            continue

        if stripped == HUMOR_MARKER:
            current_speaker = None
            continue

        if stripped.startswith("<!--"):
            errors.append(f"line {number}: use the standalone marker <!-- HUMOR -->")
            current_speaker = None
            continue

        pause_match = PAUSE_RE.fullmatch(stripped)
        if pause_match:
            current_speaker = None
            continue

        if stripped.startswith("[pause"):
            errors.append(
                f"line {number}: invalid pause; use [pause N seconds]"
            )
            current_speaker = None
            continue

        speaker_match = SPEAKER_RE.fullmatch(stripped)
        if speaker_match:
            dialogue_started = True
            current_speaker = speaker_match.group(1)
            continue

        if QUOTED_SPEAKER_RE.match(stripped):
            errors.append(
                f"line {number}: speaker label must be an unquoted name or label followed by a colon"
            )
            current_speaker = None
            continue

        # Permit wrapped text within the same speaker paragraph.
        if current_speaker and dialogue_started:
            continue

        errors.append(
            f"line {number}: expected a speaker label followed by a colon and spoken text"
        )
        current_speaker = None

    if not any(SPEAKER_RE.fullmatch(line.strip()) for line in lines):
        errors.append("transcript contains no speaker dialogue")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a podcast transcript format")
    parser.add_argument("transcript", type=Path)
    args = parser.parse_args()

    errors = validate(args.transcript)
    if errors:
        print(f"FAIL: {args.transcript}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"PASS: {args.transcript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
