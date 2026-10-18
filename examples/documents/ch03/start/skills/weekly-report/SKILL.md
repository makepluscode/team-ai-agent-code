---
name: weekly-report
description: 활동표에서 미입력과 0을 구별하며 주간 보고 작성
version: 1.7.0
---

input/DOC-004_weekly-activity.md와 input/weekly-activity.csv, input/my-instructions.md를 읽습니다.
보고 기간과 작성 시점을 적고 관측값을 합산합니다. 미입력·미확인을 0으로 채우지 않습니다.
output/DOC-009_weekly-report.r1.md에 새로 저장하고 다시 읽어 출처와 확인할 항목을 점검합니다.
기존 결과가 있으면 멈추고 새 작업 폴더에서 실행합니다.
제공 코드 경로: uv run team-work documents generate --workspace 작업폴더 --task weekly-report
Hermes 설치·스킬 등록·예약 연계는 TODO(두 기준 장비 검증). 이 파일이 있다는 사실은 등록 성공을 뜻하지 않습니다.
