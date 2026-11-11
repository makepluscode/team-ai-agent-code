# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg"]
# ///
"""6장 합성 회의 음원(MTG-001)과 구간 시각이 붙은 기준 전사문을 만든다(제작자용).

입력: tools/meeting_audio/MTG-001_script.txt(합성 대본, 한 줄 = 한 발언)
출력: examples/meetings/ch06/start/input/MTG-001_meeting.mp3(음원)
      examples/meetings/ch06/start/{input,raw}/DOC-011_transcript-fallback.md(구간 시각을 붙인 기준 전사문)
      examples/meetings/ch06/start/input/meeting-manifest.json(음원 경로·해시·길이)
실행: 환경 변수 BIZROUTER_API_KEY를 지정하고 code 폴더에서 `uv run tools/make_meeting_audio.py`.
      그 뒤 `python3 tools/make_chapter_examples.py`로 ch06 예제 폴더를 다시 만든다.
음성 합성은 BizRouter의 OpenAI 호환 음성 API(openai/gpt-4o-mini-tts)를 쓴다. 합성한 목소리이며 실제 회의 녹음이 아니다.
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path

import imageio_ffmpeg

CODE = Path(__file__).resolve().parents[1]
SCRIPT = CODE / "tools/meeting_audio/MTG-001_script.txt"
START = CODE / "examples/meetings/ch06/start"
AUDIO = "MTG-001_meeting.mp3"
API = "https://api.bizrouter.ai/v1/audio/speech"
MODEL = "openai/gpt-4o-mini-tts"
# 화자 → 목소리(한 사람은 늘 같은 목소리)
VOICES = {"매니저": "ash", "송지우": "coral", "문준서": "echo", "홍예린": "nova", "장현우": "verse"}
STYLE = "한국 회사의 짧은 업무 회의에서 말하듯 차분하고 자연스럽게, 보통 빠르기로 말하세요."
GAP = 0.7  # 발언 사이 쉬는 시간(초)


def speak(voice, text, key):
    body = json.dumps({"model": MODEL, "voice": voice, "input": text, "instructions": STYLE,
                       "response_format": "wav"}).encode()
    req = urllib.request.Request(API, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as res:
        return res.read()


def stamp(seconds):
    return f"{int(seconds // 60):02d}:{seconds % 60:04.1f}"


def main() -> int:
    key = os.environ.get("BIZROUTER_API_KEY")
    if not key:
        print("BIZROUTER_API_KEY가 없습니다."); return 1
    lines = [l.split(":", 1) for l in SCRIPT.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    # 1. 발언마다 합성하고 쉬는 시간을 넣어 한 파일로 잇는다
    frames, segments, params, now = [], [], None, 0.0
    for speaker, text in lines:
        speaker, text = speaker.strip(), text.strip()
        with wave.open(io.BytesIO(speak(VOICES[speaker], text, key))) as w:
            params = params or w.getparams()
            data = w.readframes(w.getnframes())
        length = len(data) / (params.sampwidth * params.nchannels * params.framerate)
        segments.append({"start": round(now, 1), "end": round(now + length, 1), "speaker": speaker, "text": text})
        silence = b"\0" * int(GAP * params.framerate) * params.sampwidth * params.nchannels
        frames += [data, silence]
        now += length + GAP
        print(f"{stamp(segments[-1]['start'])} {speaker}: {text}")
    pcm = io.BytesIO()
    with wave.open(pcm, "wb") as w:
        w.setparams(params._replace(nframes=0)); w.writeframes(b"".join(frames))
    # 2. mp3로 바꿔 저장한다(모노 48kbps)
    out = START / "input" / AUDIO
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "wav", "-i", "pipe:0",
                    "-ac", "1", "-b:a", "48k", str(out)], input=pcm.getvalue(), check=True)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    # 길이는 저장한 mp3를 다시 읽어 잰다(인코더가 붙이는 여백 포함, 재생 프로그램이 보여 주는 값과 같게)
    probe = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(out)], capture_output=True, text=True)
    h, m, sec = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe.stderr).groups()
    duration = round(int(h) * 3600 + int(m) * 60 + float(sec), 1)
    # 3. 구간 시각을 붙인 기준 전사문과 회의 정보를 쓴다
    body = "\n".join(f"[{stamp(s['start'])}–{stamp(s['end'])}] {s['speaker']}: {s['text']}" for s in segments)
    doc = f"""---
document_id: "DOC-011"
revision: "r1"
created_at: "2026-10-12T09:00:00+09:00"
effective_at: "2026-10-12T09:00:00+09:00"
state: "초안"
source_refs: ["MTG-001"]
data_kind: "authored-transcript"
---

# MTG-001 회의 기준 전사문

> 저자가 쓴 합성 대본이며, 같은 대본으로 합성 음원 input/{AUDIO}(AI 음성, 실제 회의 녹음 아님)을 만들었습니다. 구간 시각은 합성할 때 잰 값입니다. 로컬 전사 결과와 대조하는 기준으로 씁니다.

{body}
"""
    for folder in ("input", "raw"):
        (START / folder / "DOC-011_transcript-fallback.md").write_text(doc, encoding="utf-8")
    manifest = {
        "meeting_id": "MTG-001", "data_kind": "synthetic",
        "audio": f"input/{AUDIO}", "audio_sha256": digest, "audio_duration_seconds": duration,
        "audio_kind": "AI 음성 합성(실제 회의 녹음 아님)", "speakers": sorted({s["speaker"] for s in segments}),
        "fallback": "DOC-011_transcript-fallback.md", "fallback_kind": "authored-transcript",
        "transcription_executed": False, "speaker_identification": False,
    }
    (START / "input/meeting-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"저장: {out.relative_to(CODE)} ({duration}초, {out.stat().st_size // 1024}KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
