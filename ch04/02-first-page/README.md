# 02-first-page: 첫 위키 페이지 정리

헤르메스가 wiki-curator 역할로 초기 원본 네 건을 읽어 새 동료 안내 페이지의 변경안을 output/wiki-draft/에 쓰고,
사람이 확인한 뒤 main.py가 wiki/에 적용합니다. 책 4.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch04/02-first-page
hermes chat --query-file prompt.md
uv run main.py preview
uv run main.py apply
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| AGENTS.md | 위키 정리 규칙. 변경안은 output/wiki-draft/에 쓰도록 정했습니다 |
| raw/ | 초기 원본 네 건과 근거 묶음 |
| wiki/ | 위키 페이지 폴더(적용 전에는 비어 있음) |
| prompt.md | 첫 페이지 정리 지시문 |
| expected/wiki/ | 저자가 편집한 비교용 페이지 |
| check.py | 원본 보존·페이지 저장 확인과 사람이 볼 줄 표시 |
| main.py | 단계 preview / apply / search. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


apply는 wiki/가 마지막 적용 뒤에 바뀌었으면 충돌로 멈추고, 적용 전 위키를 output/wiki-before-N/에 남깁니다.
적용한 변경안 폴더는 output/wiki-draft-applied-N/으로 옮겨집니다.
