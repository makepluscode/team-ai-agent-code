# 03-change-memo: 동료의 변경 메모 반영

자료 담당 M03이 쓴 일정 변경 메모(DOC-010@r1)를 raw/에 원본으로 등록하고, 매니저의 헤르메스가 wiki-curator로 위키 변경안을 쓴 뒤
사람이 확인하고 적용합니다. 책 5.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch05/03-change-memo
uv run main.py register
hermes chat --query-file prompt.md
uv run main.py preview
uv run main.py apply
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/DOC-010_schedule-change.md | M03이 쓴 일정 변경 메모(등록 전) |
| raw/·wiki/ | 4장까지의 원본과 위키 |
| prompt.md | 변경 메모 반영 지시문 |
| expected/wiki/ | 비교용 위키 페이지 |
| check.py | 원본 보존·등록·페이지 저장 확인 |
| main.py | 단계 register / preview / apply. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |
