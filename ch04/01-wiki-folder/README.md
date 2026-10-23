# 01-wiki-folder: 로컬 위키 폴더와 정리 규칙 확인

4장 시작 자료(초기 원본 네 건과 주간 보고 근거 묶음)로 만든 로컬 위키 폴더입니다. 헤르메스가 규칙 파일(AGENTS.md)을
읽고 원본의 문서 ID·버전·상태를 확인합니다. 책 4.1~4.2절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch04/01-wiki-folder
hermes chat --query-file prompt.md
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| AGENTS.md | 위키 정리 규칙(작업 폴더 규칙). 이 폴더에서 헤르메스를 실행하면 자동으로 읽힙니다 |
| raw/ | 초기 원본 네 건과 주간 보고 근거 묶음(report-input/). 수정하지 않습니다 |
| wiki/ | 위키 페이지 폴더(아직 비어 있음) |
| input/ | 원본 등록 기록(raw-registry.json·report-source-map.json) |
| prompt.md | 규칙 요약과 원본 점검 지시문 |
| check.py | 원본이 그대로인지 확인합니다 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |
