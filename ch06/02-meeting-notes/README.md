# 02-meeting-notes: 회의 결정과 할 일 추출

기준 전사문에서 확정 결정·할 일·취소·미정을 구분한 회의록 초안(DOC-012)을 헤르메스가 작성합니다. 사람이 원음 구간과 대조해
확인해야 위키에 등록할 수 있습니다. 책 6.3절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch06/02-meeting-notes
hermes chat --query-file prompt.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/DOC-011_transcript-fallback.md | 기준 전사문(합성) |
| input/meeting-manifest.json | 회의 정보 |
| wiki/ | 5장까지 갱신된 위키 |
| prompt.md | 회의록 초안 지시문 |
| expected/DOC-012_meeting-notes.md | 비교용 회의록 |
| check.py | 원본 보존·결과 저장 확인 |
