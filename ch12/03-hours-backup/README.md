# 03-hours-backup: 업무시간 운영과 백업·복구

평일 업무시간(09~18시) 안에서만 팀 작업을 실행하고 한 명의 담당만 실행하도록 잠그는 동작, 백업과 새 폴더 복구를 연습한 뒤
헤르메스가 월말 마감 보고서를 씁니다. 책 12.4절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch12/03-hours-backup
uv run main.py setup
uv run main.py gate
uv run main.py run
uv run main.py backup
uv run main.py restore
hermes chat --query-file prompt.md
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/business-hours.json | 업무시간 규칙 |
| input/month-end-snapshot.json | 월말 비교 자료(저자 편집) |
| prompt.md | 월말 보고서 지시문 |
| check.py | 원본 보존·보고서 저장 확인 |
| main.py | 단계 setup / gate / run / backup / restore / json / list. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


백업은 작업 폴더 밖의 새 폴더에만 만들고, 복구도 새 폴더에만 합니다. 기존 폴더를 덮어쓰지 않습니다.
