# 04-weekly-schedule: 주간 보고 예약 하나와 실행 확인

03-weekly-skill에서 등록한 weekly-report 스킬을 매주 금요일 17시에 실행하는 개인 연습용 예약 하나를 등록하고, 즉시 실행으로 결과 파일을 확인하는 예제입니다. 책 3.4절에 대응합니다.

## 시작 조건

weekly-report 스킬이 내 헤르메스에 등록돼 있어야 합니다(`hermes skills list`에 local로 표시). 없으면 03-weekly-skill의 등록 명령을 먼저 실행합니다.

## 실행 방법

```bash
cd ~/agent-work/ch03/04-weekly-schedule
hermes cron create "0 17 * * 5" --name weekly-report-practice --skill weekly-report --workdir "$PWD" "$(cat prompt.md)"
hermes cron list
hermes cron run weekly-report-practice
uv run check.py
hermes cron pause weekly-report-practice
```

- check.py는 output/scheduled/에서 오늘 날짜가 붙은 보고를 찾습니다. 다른 날의 결과는 `uv run check.py 2026-10-23`처럼 날짜를 넘깁니다.
- 연습이 끝나면 예약을 멈추거나(`pause`) 지웁니다(`hermes cron remove weekly-report-practice`). 등록 명령을 다시 실행하기 전에는 `hermes cron list`로 같은 이름의 예약이 이미 있는지 확인합니다(같은 이름 재등록 동작은 검증하지 않았습니다).
- 정해진 시각의 자동 실행은 게이트웨이가 켜져 있어야 합니다(`hermes cron status`).

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 예약 실행이 쓰는 요청(저장 위치에 실행 날짜를 붙임) |
| input/ | 3.2절과 같은 회의 노트·업무 노트 정리본, 입력 묶음, 관측 기준 |
| expected/DOC-009_weekly-report.r1.md | 비교용 주간 보고 |
| check.py | 원본 보존과 날짜별 결과 저장을 확인합니다 |
