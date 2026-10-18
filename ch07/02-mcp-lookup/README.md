# 02-mcp-lookup: 조회 전용 MCP 연결

요청 기록 DB를 조회만 하는 MCP 서버를 헤르메스에 등록하고, 헤르메스가 get_request·get_roles 도구로 요청과 담당 기준을 읽게 합니다.
서버에는 쓰기 도구가 없습니다. 책 7.3절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch07/02-mcp-lookup
uv run main.py setup
hermes mcp add team-requests --command uv --args run --directory "$PWD" main.py mcp
hermes mcp test team-requests
hermes chat --query-file prompt.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/internal-requests.json | 내부 요청 8건(합성) |
| input/members.json | 역할 명부 M01~M05 |
| input/snapshot.json | 독립 시작 시점의 업무·사건 기록 |
| raw/ | 6장까지의 원본(문서 버전별) |
| prompt.md | MCP 도구 조회 지시문 |
| main.py | setup: DB 준비·접수 / mcp: 조회 전용 서버 |
| pyproject.toml | MCP 서버 실행에 필요한 mcp 패키지 |
| check.py | 원본 보존·접수 건수 확인 |


서버는 표준 입출력(stdio)으로 헤르메스와 주고받으므로 터미널에서 직접 켜 두지 않습니다. 연습이 끝나면 hermes mcp remove team-requests로 등록을 지웁니다.
