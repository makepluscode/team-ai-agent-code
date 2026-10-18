# 01-meeting-input: 회의 입력 자료와 로컬 전사

MTG-001 회의의 입력 자료(회의 정보·용어표·기준 전사문)를 점검하고, 음원이 있으면 로컬 Whisper(faster-whisper)로 전사하는
예제입니다. 이 책의 합성 회의 음원은 아직 제작 전이어서 기준 전사문(DOC-011@r1)으로 6.3절을 이어 갑니다. 책 6.1~6.2절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch06 ~/agent-work/ch06
cd ~/agent-work/ch06/01-meeting-input
hermes chat --query-file prompt.md
uv run --extra transcription main.py transcribe <음원 경로>
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/meeting-manifest.json | 회의 ID·음원·해시·대안 전사문 정보 |
| input/glossary.txt | 전사 힌트용 용어표 |
| input/DOC-011_transcript-fallback.md | 저자가 쓴 기준 전사문(합성, 원음 대조 전) |
| prompt.md | 입력 점검 지시문 |
| transcript.md | 전사 결과와 기준 전사문 대조 지시문(음원이 있을 때) |
| main.py | transcribe: 로컬 전사(선택, faster-whisper 필요) |
| check.py | 원본 보존 확인 |


전사는 CPU·base·int8 구성을 검토 기준으로 둡니다. 실제 음원의 전사와 원음 청취 대조는 두 기준 장비에서 TODO(검증)입니다.
