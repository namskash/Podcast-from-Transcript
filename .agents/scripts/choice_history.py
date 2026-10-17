#!/usr/bin/env python3
"""Stage transcript choices and persist them to usage history."""

from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path

HISTORY_PATH = Path("docs/choice-selection-history.json")
TMP_DIR = Path("tmp")


def read_json(path: Path, default):
    if not path.exists():
        return default
    content = path.read_text(encoding="utf-8").strip()
    return default if not content else json.loads(content)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    begin_parser = subparsers.add_parser("begin")
    begin_parser.set_defaults(func=begin)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("key")
    list_parser.set_defaults(func=list_choices)

    stage_parser = subparsers.add_parser("stage")
    stage_parser.add_argument("stage_file", type=Path)
    stage_parser.add_argument("key")
    stage_parser.add_argument("value")
    stage_parser.set_defaults(func=stage_choice)

    persist_parser = subparsers.add_parser("persist")
    persist_parser.add_argument("stage_file", type=Path)
    persist_parser.set_defaults(func=persist_choices)

    args = parser.parse_args()
    return args.func(args)


def begin(args: argparse.Namespace) -> int:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    stage_file = TMP_DIR / f"choice-selections-{secrets.token_hex(8)}.json"
    write_json(stage_file, {})
    print(stage_file)
    return 0


def list_choices(args: argparse.Namespace) -> int:
    data = read_json(HISTORY_PATH, {})
    choices = data.get(args.key, {})
    ordered = sorted(choices.items(), key=lambda item: (-item[1], item[0]))
    print(json.dumps(dict(ordered), ensure_ascii=False))
    return 0


def stage_choice(args: argparse.Namespace) -> int:
    staged = read_json(args.stage_file, {})
    staged.setdefault(args.key, []).append(args.value)
    write_json(args.stage_file, staged)
    return 0


def persist_choices(args: argparse.Namespace) -> int:
    staged = read_json(args.stage_file, {})
    history = read_json(HISTORY_PATH, {})

    for key, values in staged.items():
        choices = history.setdefault(key, {})
        for value in values:
            choices[value] = int(choices.get(value, 0)) + 1

    write_json(HISTORY_PATH, history)
    args.stage_file.unlink(missing_ok=True)
    print(json.dumps(history, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
