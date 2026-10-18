# 02-team-dashboard: 팀 대시보드 조회와 동료 접속

공동 기록 DB로 조회 전용 팀 대시보드를 띄우고, 헤르메스가 화면과 대조할 현황 요약과 동료 접속 안내문을 만듭니다.
11장 기본 모드에서는 새 요청·상태 변경이 거부됩니다. 책 11.2~11.4절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch11/02-team-dashboard
uv run main.py setup
hermes chat --query-file setup-check.md
uv run main.py serve
hermes chat --query-file prompt.md
hermes chat --query-file peer.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/snapshot.json | 10/19 기준 공동 기록 |
| wiki/·raw/ | 근거 위키와 원본 |
| setup-check.md | 설정 점검 지시문 |
| prompt.md | 현황 요약 지시문 |
| peer.md | 동료 접속 안내 지시문 |
| main.py | setup / serve: 조회 대시보드 / share: 동료 접속용 / list |
| pyproject.toml | 대시보드에 필요한 fastapi·uvicorn |
| check.py | 원본 보존·기록 건수·요약 저장 확인 |


serve와 share는 끌 때까지 실행됩니다(Ctrl+C). 다른 터미널에서 hermes를 실행합니다. 사내 접속 범위와 방화벽 설정은 11.4절과 TODO(검증)를 따릅니다.
