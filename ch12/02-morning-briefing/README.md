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
| slack-briefing.md | 팀 Slack 채널로 보낼 브리핑 지시문(선택, 12.3.3절) |
| check.py | 원본 보존·브리핑 저장 확인 |
| main.py | 단계 setup / briefing / json / list. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


## 선택: 팀 Slack 채널로 브리핑 받기(12.3.3절)

공동 컴퓨터의 팀 헤르메스 한 대에만 연결합니다. Slack 앱 만들기와 토큰 발급은 책 12.3.3절을 따르고, 토큰은 ~/.hermes/.env에만 둡니다.

```bash
hermes slack manifest --agent-view --write
hermes gateway setup
hermes gateway restart
hermes cron create "0 9 * * 1-5" --name morning-briefing --deliver slack --workdir "$PWD" "$(cat slack-briefing.md)"
hermes cron run morning-briefing
hermes cron list
hermes cron pause morning-briefing
```

실제 Slack 연결과 전송은 기준 장비에서 확인하지 않았습니다(TODO(검증)). 연결하지 않아도 prompt.md와 check.py로 이 예제를 마칠 수 있습니다.
