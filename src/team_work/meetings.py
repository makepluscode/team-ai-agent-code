"""Optional real transcription, with explicitly authored fallback text."""

import hashlib
import time
from pathlib import Path

from .io import read_text, write_json
from .workspace import verify


def transcribe(workspace, audio):
    work, audio = Path(workspace).resolve(), Path(audio).resolve()
    verify(work)
    if not audio.is_file():
        raise ValueError(
            "음원이 없습니다. 제공 합성 전사 대안으로 이어 가세요. 전사는 미완료입니다."
        )
    target = work / "output/transcript.json"
    if target.exists():
        raise ValueError("기존 전사 결과를 보존합니다.")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ValueError(
            "선택 전사 의존성이 없습니다. uv sync --extra transcription 또는 제공 전사 대안을 쓰세요. 두 기준 장비 검증은 TODO(검증)입니다."
        ) from None
    started = time.monotonic()
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio), language="ko", initial_prompt=read_text(work / "input/glossary.txt")
    )
    rows = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    write_json(
        target,
        {
            "data_kind": "actual-transcription",
            "meeting_id": "MTG-001",
            "audio_sha256": hashlib.sha256(audio.read_bytes()).hexdigest(),
            "model": "base",
            "device": "cpu",
            "compute_type": "int8",
            "segments": rows,
            "language": info.language,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "speaker_identification": False,
        },
    )
    return {"transcript": str(target), "human_audio_comparison": "확인 필요"}
