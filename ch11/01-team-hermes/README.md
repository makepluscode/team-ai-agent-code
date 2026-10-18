# 01-team-hermes: 헤르메스 한 대로 모으기

팀 공동 작업을 사무실 공동 컴퓨터의 헤르메스 한 대로 모읍니다. SOUL.md로 팀 에이전트 이름(프라이데이)을 붙이고, 공동 기록 DB와
팀 작업 담당·업무시간을 준비합니다. 책 11.1절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch11 ~/agent-work/ch11
cd ~/agent-work/ch11/01-team-hermes
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig
cp SOUL.md ~/.hermes/SOUL.md
uv run main.py setup
hermes chat --query-file prompt.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| SOUL.md | 팀 에이전트 프라이데이의 기본 규칙(공동 컴퓨터의 ~/.hermes/SOUL.md로 복사) |
| input/snapshot.json | 10/19 기준 공동 기록(요청 10·업무 12) |
| input/business-hours.json | 업무시간 규칙 |
| wiki/·raw/ | 9장까지의 위키와 원본 |
| prompt.md | 이관 점검표 지시문 |
| main.py | setup: DB 준비·담당 지정 / gate: 업무시간 확인 |
| check.py | 원본 보존·공동 기록 건수 확인 |


SOUL.md 복사는 공동 컴퓨터에서만 합니다. 매니저 개인 컴퓨터의 자비스와 이름이 구별됩니다.
