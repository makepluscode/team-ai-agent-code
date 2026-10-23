# 02-review-and-fix: 수정 요청과 다시 확인

헤르메스가 수정 문서(DOC-007@r3·DOC-009@r2)와 확인 질문 기록을 쓰고, 사람이 읽은 뒤 main.py로 검토 6건과 상태 전이를 기록합니다.
상태는 정해진 경로(확인 대기 → 수정 필요 → 진행 → 확인 대기 → 완료)로만 바뀌고, 완료에는 사람 확인 표시가 필요합니다. 책 9.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch09/02-review-and-fix
uv run main.py setup
hermes chat --query-file prompt.md
uv run main.py review
uv run main.py task-002
uv run main.py list
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

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
| expected/review-corrections/ | 비교용 수정본·질문 기록 |
| check.py | 원본 보존·검토 6건·TASK-002 완료 확인 |
| main.py | 단계 setup / review / task-002 / list. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


review는 검토 6건을 실행할 때마다 한 건씩 기록합니다. 화면에 나온 검토 내용과 헤르메스 결과(output/)를 대조하고 y로 답합니다. task-002도 실행할 때마다 한 단계씩(수정 필요 → 진행 → 확인 대기 → 완료) 옮기며, 진행 위치는 state/progress.json에 남습니다.
