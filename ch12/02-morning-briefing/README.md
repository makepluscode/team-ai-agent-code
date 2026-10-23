# 02-morning-briefing: 회의록과 아침 브리핑 통합

밤사이 접수된 일과 미완료 업무를 원문 근거와 함께 아침 9시 브리핑으로 묶습니다. main.py가 업무시간 기준 브리핑 자료를 만들고,
헤르메스가 대시보드 패널용 문서로 정리합니다. 책 12.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch12/02-morning-briefing
uv run main.py setup
uv run main.py briefing
hermes chat --query-file prompt.md
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/snapshot.json | 공동 기록 |
| input/business-hours.json | 업무시간 규칙(월~금 09~18시) |
| prompt.md | 브리핑 문서 지시문 |
| check.py | 원본 보존·브리핑 저장 확인 |
| main.py | 단계 setup / briefing / json / list. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |
