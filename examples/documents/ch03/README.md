# 3장 회의 자료 주간 보고와 재사용

일반 폴더에서 온보딩 가이드 한 건을 짧게 작성하고 회의 자료로 주간 보고를 만듭니다. DOC-008은 삭제·결번입니다.
독립 시작 input/organized/는 2장 정리본과 같은 8개이며 보고 입력은 텍스트6개만 사용합니다.
DOC-004_weekly-meetings.md는 묶음 목록입니다. 사진·확인 필요 제외, 지난주는 변화 비교만 합니다.

```bash
uv run team-work prepare --chapter 3 --workspace /tmp/book-ch03
uv run team-work documents generate --task onboarding-guide --workspace /tmp/book-ch03
uv run team-work documents generate --task weekly-report --workspace /tmp/book-ch03
uv run team-work verify --workspace /tmp/book-ch03
```

완료 기준: 항목키별 중복 제외 관측 완료4건·지난주 대비 변화·남은 액션 담당/기한/상태/출처·상태 미기재/미입력과 메모 범위0건 구별.
관측 기간10/05~10/09·기준10/07은 snapshot.json에서 읽고 금요일 예약 실행 시각으로 바꾸지 않습니다.
스킬은 start/skills/weekly-report, 제공 실행기는 operations/personal-weekly-report를 참조합니다.
예약 등록·실제 실행·관측 기준을 구별합니다. 실습 뒤 중지하고 새 폴더에서 수동 복구합니다.
새 회의 예제의 상용 생성·헤르메스 스킬·금요일 예약·두 기준 장비 검증 및 관련 화면 재촬영은 TODO입니다.
