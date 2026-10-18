# 01-dashboard-work: 대시보드에서 지시와 상태 변경

대시보드에서 새 요청(REQ-011)을 받아 업무 TASK-013을 만들고, 상태를 정해진 경로로만 바꿉니다. 완료에는 사람 확인 표시가 필요합니다.
대시보드의 버튼과 main.py의 task-013 단계는 같은 상태 전이 함수를 씁니다. 책 12.1~12.2절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch12 ~/agent-work/ch12
cd ~/agent-work/ch12/01-dashboard-work
uv run main.py setup
uv run main.py serve
uv run main.py intake
hermes chat --query-file prompt.md
uv run main.py task-013
hermes chat --query-file history.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/dashboard-request.json | 새 요청 REQ-011(합성) |
| input/snapshot.json | 10/19 기준 공동 기록 |
| prompt.md | 지시 레코드 지시문 |
| history.md | 상태 이력표 지시문 |
| main.py | setup / serve: 쓰기 대시보드 / intake: 파일로 접수 / task-013: 상태 전이 / json / list |
| check.py | 원본 보존·요청 11·업무 13 확인 |
