# 6장 예약 실행과 비용

『팀 AI 에이전트 실전』 6장의 실습 안내입니다. 업무시간에만 도는 예약 작업과 아침 브리핑, 사용량·비용 기록을 만들고, 정한 운영 기준을 위키 결정 페이지로 남깁니다.

- 원고: `content/ch06_scheduling-cost_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/)(업무시간·밤사이 접수·사용량 예시·가격표), 지시문 [prompts/](prompts/), 실습 정의 [tasks.json](tasks.json), 비교용 결과 [completed/](completed/), 위키 원본 [wiki-raw/](wiki-raw/)
- 예약 진입점: [scheduled_job.py](scheduled_job.py)
- 6장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)

> 확인 범위: 업무시간 판정·날짜별 보관·중복 방지·위키 받기 단계와 상용 API 실행 기록 집계를 확인했습니다. 헤르메스 예약 등록·게이트웨이 자동 시작·절전 중 누락은 기준 장비에서 확인 전입니다.

예약은 모두 **PM의 헤르메스 한 대**에 둡니다.

| 예약 | 시각(Asia/Seoul) | 예약안 |
|---|---|---|
| 아침 브리핑 | 평일 09:00 | [../ch03/completed/morning-job.json](../ch03/completed/morning-job.json) |
| 주간 회고 초안 | 금요일 16:00 | [../ch03/completed/friday-job.json](../ch03/completed/friday-job.json) |
| 위키 드라이브 내보내기 | 금요일 16:30 | [completed/friday-export-job.json](completed/friday-export-job.json) |

## 6.1 업무시간 예약 실행

```bash
python3 run.py run ch06-business-hours --workspace work --at 2026-10-08T09:00:00+09:00
python3 ch06/scheduled_job.py --workspace work --task ch06-morning-briefing --at 2026-10-08T09:00:00+09:00            # 실행안만
python3 ch06/scheduled_job.py --workspace work --task ch06-morning-briefing --at 2026-10-09T09:00:00+09:00 --execute  # 휴무일: 실행 안 함
python3 run.py run ch06-friday-export --workspace work                                                                # 금요일 내보내기 예약안
```

`scheduled_job.py`의 순서: 업무시간 판정 → 같은 날 성공 결과가 있으면 보존하고 멈춤 → **위키 받기 전용**(`wiki_sync.py pull-only`, 종료 코드 2면 작업을 만들지 않고 멈춘 이유만 기록. 원격이 없는 연습 위키는 건너뜀) → 날짜별 폴더(`work/scheduled/<날짜>/`)에 실행·검사. `--engine api`로 헤르메스 대신 상용 API를 씁니다.

경계 시각: 10/08 08:59 대기, 09:00 실행, 17:59 실행, 18:00 대기, 10/09 휴무일, 10/10 토요일. UTC `2026-10-08T00:00:00Z`는 한국 09:00이라 실행합니다.

## 6.2 아침 브리핑

| 항목 | 내용 |
|---|---|
| 실습 ID | `ch06-morning-briefing` |
| 지시문 | [prompts/ch06-morning-briefing.txt](prompts/ch06-morning-briefing.txt) |
| 읽는 것 | `overnight.json`(10/07 18:00~10/08 09:00 접수 2건), 위키 고객 페이지 |
| 자동 확인 | 'IN-BB-001'·'IN-DP-001'·'확인 필요' |

```bash
python3 run.py run ch06-morning-briefing --workspace work --engine api
```

브리핑 본문은 팀 채널에 그대로 보내는 짧은 확인 목록입니다. 위키에는 넣지 않습니다. 담당 직군을 배정하지 않습니다.

## 6.3 사용량과 처리 기록

```bash
python3 run.py run ch06-usage --workspace work            # 합성 예시(실패·재시도 포함, 단가 null이면 합계 null)
python3 run.py run ch06-usage-measured --workspace work   # 이 작업 폴더에서 --engine api로 실행한 실제 기록 집계
```

`work/run-history.jsonl`에는 실습마다 시각·성공/실패·경과시간이 쌓이고, `--engine api`로 실행한 줄에는 공급자·모델·입력/출력 토큰(제미나이는 thinking 토큰 포함)이 들어갑니다. 헤르메스 경로는 토큰을 알 수 없어 null입니다. 가격표([start/price-card.json](start/price-card.json))의 단가가 확인 전(null)이라 비용 합계도 null이며 0원으로 계산하지 않습니다.

## 6.4 비용 줄이기와 운영 기준 — `ch06-ops-record`

운영 기준 원본 [wiki-raw/20261008_TEAM_operations.md](wiki-raw/20261008_TEAM_operations.md)를 넣고 결정 페이지 `wiki/decisions/20261008_operating-rules.md`로 정리합니다.

```bash
python3 run.py run ch06-ops-record --workspace work --engine api
```

자동 검사: 결정 페이지에 09:00·16:30·2026-10-09·'확인 필요'(측정 전 값). 비교 측정(입력 범위·모델·캐시)은 실측 전이라 수치를 넣지 않습니다.

## 되돌아갈 자리

- 업무시간 설정: [start/business-hours.json](start/business-hours.json)
- 판정 코드: [../run.py](../run.py)의 `business_time`·`cost_summary`, 예약 진입점의 `scheduled`·`pull_wiki`
