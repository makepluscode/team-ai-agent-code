"""Shared UTF-8 IO with explicit overwrite protection."""

import json
from pathlib import Path


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def write_new(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    except FileExistsError:
        raise ValueError(f"기존 파일을 보존합니다: {path}") from None
    return path


def write_json(path, data):
    return write_new(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
