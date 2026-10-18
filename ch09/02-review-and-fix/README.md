# 02-review-and-fix: 수정 요청과 다시 확인

헤르메스가 수정 문서(DOC-007@r3·DOC-009@r2)와 확인 질문 기록을 쓰고, 사람이 읽은 뒤 main.py로 검토 6건과 상태 전이를 기록합니다.
상태는 정해진 경로(확인 대기 → 수정 필요 → 진행 → 확인 대기 → 완료)로만 바뀌고, 완료에는 사람 확인 표시가 필요합니다. 책 9.3절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch09/02-review-and-fix
uv run main.py setup
hermes chat --query-file prompt.md
uv run main.py review
uv run main.py task-002
uv run main.py list
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/internal-requests.json | 내부 요청 8건(합성) |
| input/members.json | 역할 명부 M01~M05 |
| input/snapshot.json | 독립 시작 시점의 업무·사건 기록 |
| raw/ | 6장까지의 원본(문서 버전별) |
| input/reviews/ | 검토 사례 6건(REV-001~006)의 전후 참조·이유·근거 |
| input/review-fixtures/REV-002-input.md | 오류를 일부러 넣은 주간 보고 파생 자료(현재 사실 아님) |
| input/review-rules.json | 상태 전이와 사람 확인 기준 |
| prompt.md | 수정 문서·질문 기록 지시문 |
| main.py | setup / review: 검토 6건 기록 / task-002: 상태 전이 / list |
| expected/review-corrections/ | 비교용 수정본·질문 기록 |
| check.py | 원본 보존·검토 6건·TASK-002 완료 확인 |


review와 task-002는 사람 확인을 기록하는 명령입니다. 헤르메스가 만든 결과를 직접 읽고 맞는지 확인한 뒤 실행합니다.
