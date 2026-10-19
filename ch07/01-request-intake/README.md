# 01-request-intake: 내부 요청 접수와 처리 기록

내부 요청 8건을 같은 형식으로 접수해 요청 기록 DB(state/requests.sqlite3)에 남기고, 요청·업무·사건 기록을 목록으로 확인합니다.
접수는 main.py가 확정적으로 처리하고, 헤르메스는 접수 형식 점검(prompt.md)과 처리 현황 표(status.md)를 맡습니다. 책 7.1~7.2절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch07 ~/agent-work/ch07
cd ~/agent-work/ch07/01-request-intake
uv run main.py intake
hermes chat --query-file prompt.md
hermes chat --query-file status.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/internal-requests.json | 내부 요청 8건(합성) |
| input/members.json | 역할 명부 M01~M05 |
| input/snapshot.json | 독립 시작 시점의 업무·사건 기록 |
| raw/ | 6장까지의 원본(문서 버전별) |
| prompt.md | 접수 형식 점검 지시문 |
| status.md | 처리 현황 표(DOC-014@r1) 지시문 |
| check.py | 원본 보존·접수 건수 확인 |
| main.py | 단계 intake / list / json. 인자 없이 실행하면 할 일과 단계를 안내 |


다시 할 때는 새 사본을 만듭니다. 같은 폴더에서 intake를 두 번 실행하면 '이미 초기화한 상태'로 멈춥니다.
