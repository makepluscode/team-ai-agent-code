# 12장 독립 실습

합성 입력과 편집 비교 결과(author-reference)입니다. 저자 전건 검수 전이며 실제 모델 응답·실서비스 연결·두 기준 장비 검증을 뜻하지 않습니다.

코드 경로(code/에서 실행):

```sh
uv run team-work prepare --chapter 12 --workspace /tmp/merry-ch12
uv run team-work requests init --workspace /tmp/merry-ch12
uv run team-work requests list --workspace /tmp/merry-ch12
```

지시문 경로: 준비한 prompts/task.md를 헤르메스에 파일로 입력하거나 복사합니다. input/의 시작 자료와 raw/를 읽고 output/에 새 결과를 저장합니다. 준비 시 reference/는 복사하지 않습니다.

복구: 기존 작업 폴더를 보존하고 다른 빈 폴더에 다시 prepare·init합니다. DB를 수동 수정하지 않습니다. 완료 기준은 아래의 장별 확인을 따릅니다.

```sh
uv run team-work requests intake --workspace /tmp/merry-ch12 --input /tmp/merry-ch12/input/dashboard-request.json
uv run team-work dashboard --workspace /tmp/merry-ch12 --writable
```

화면의 업무 지시 폼 또는 제공 요청 파일로 REQ-011·TASK-013을 접수합니다. 파일과 화면을 동시에 중복 접수해도 새 업무를 늘리지 않습니다. 같은 상태 기록에서 TASK-013을 진행→확인 대기→수정 필요→진행→확인 대기→완료로 옮깁니다. actor·이유·근거·현재 상태가 필요하며 완료는 사람 확인 체크가 필요합니다. 월말 편집 비교 기록은 reference/month-end-snapshot.json입니다. 요청11·업무13, 완료6·진행2·확인 대기5를 확인합니다. 실제 한 달 운영·시간·비용은 미측정(null)입니다. 야간 작업을 자동 실행하지 않습니다.

단일 담당과 업무시간·아침 확인의 로컬 제공 경로:

```sh
uv run team-work team-ops init --workspace /tmp/merry-ch12 --owner M01
uv run team-work team-ops gate --workspace /tmp/merry-ch12 --at 2026-10-19T09:00:00+09:00
uv run team-work team-ops briefing --workspace /tmp/merry-ch12 --at 2026-10-19T09:00:00+09:00
uv run team-work team-ops run-due --workspace /tmp/merry-ch12 --owner M01 --at 2026-10-19T09:00:00+09:00
```

--at는 제공 합성 시각 검사입니다. 생략하면 실행 시각으로 검사하고 관측 실행으로 남깁니다. input/business-hours.json이 있으면 그 설정, 없으면 Asia/Seoul·월~금09:00 이상18:00 미만을 사용합니다. 공휴일 자동 조회는 하지 않습니다. 브리핑은 이전 업무일18:00~당일09:00 접수·확인대기·기한초과의 ID와 원문 근거를 집계하며 모델 문장을 생성하지 않습니다. run-due는 업무시간 밖이면 건너뛰고 업무시간 안에서 브리핑을 output/briefing-RUN-*.json에 저장합니다.

한 작업 폴더의 state/team-owner.json에 한 명을 등록하고 team-operation.lock이 있으면 중복 실행을 거부합니다. 여러 PC의 별도 폴더를 동시에 실행하는 분산 잠금은 제공하지 않습니다. 중단 후에는 실제 실행 프로세스가 끝난 것을 확인하고 `team-ops release-lock --workspace /tmp/merry-ch12 --owner M01 --confirm`으로 복구합니다. 이 경로는 수동 실행이며 Hermes background 팀 예약의 실제 등록·Gmail 연결은 TODO(검증)입니다.
