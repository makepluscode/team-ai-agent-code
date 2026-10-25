# 03-weekly-schedule: 주간 보고 예약 하나와 실행 확인

02-weekly-skill에서 등록한 weekly-report 스킬을 매주 금요일 17시에 실행하는 개인 연습용 예약 하나를 등록하고, 즉시 실행으로 결과 파일을 확인하는 예제입니다. 책 3.3절에 대응합니다.

## 시작 조건

weekly-report 스킬이 내 헤르메스에 등록돼 있어야 합니다(`hermes skills list`에 local로 표시). 없으면 02-weekly-skill의 등록 명령을 먼저 실행합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch03/03-weekly-schedule
hermes cron create "0 17 * * 5" --name weekly-report-practice --skill weekly-report --workdir "$PWD" "$(cat prompt.md)"
hermes cron list
hermes cron run weekly-report-practice
ls output/scheduled
hermes cron pause weekly-report-practice
```

- 예약 실행은 output/scheduled/에 실행 날짜가 붙은 보고를 남깁니다. 실행 전후의 `ls` 결과로 이번 실행의 파일을 구별하고 `cat`으로 엽니다.
- 연습이 끝나면 예약을 멈추거나(`pause`) 지웁니다(`hermes cron remove weekly-report-practice`). 등록 명령을 다시 실행하기 전에는 `hermes cron list`로 같은 이름의 예약이 이미 있는지 확인합니다(같은 이름 재등록 동작은 검증하지 않았습니다).
- 정해진 시각의 자동 실행은 게이트웨이가 켜져 있어야 합니다(`hermes cron status`).

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 결과 폴더(output/)를 지운 뒤 실행 방법을 다시 따라 합니다. 헤르메스 설정(~/.hermes)은 바뀌지 않습니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 예약 실행이 쓰는 요청(저장 위치에 실행 날짜를 붙임) |
| input/ | 3.1절과 같은 회의 노트·업무 노트 정리본, 입력 묶음, 관측 기준 |
| expected/DOC-009_weekly-report.r1.md | 비교용 주간 보고 |
| reset.py | 결과 폴더(output/)를 지워 처음부터 다시 하기. ~/.hermes는 바꾸지 않습니다 |

## 확인할 것

결과 파일을 열어 원본(input/)과 대조합니다.

- 관측 기준 시각이 input/snapshot.json의 값 그대로인가
- 완료가 항목키 ITEM-001~004의 네 건이고, 대화의 재언급을 다시 세지 않았는가
- ITEM-005·006이 완료가 아니라 제안·상태 미기재로 남았는가
- 보고 업무 TASK-001이 '확인 대기'인가
