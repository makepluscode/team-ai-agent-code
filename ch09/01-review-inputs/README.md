# 01-review-inputs: 검토 대상 점검과 확인 기준

사람이 검토할 6사례의 근거를 헤르메스가 점검하고(prompt.md) 조치 계획을 세웁니다(plan.md). 오류를 일부러 넣은 파생 자료는
현재 사실이 아닙니다. 책 9.1~9.2절에 대응합니다.

## 실행 방법

```bash
mkdir -p ~/agent-work && cp -r --update=none ~/team-ai-agent/code/ch09 ~/agent-work/
cd ~/agent-work/ch09/01-review-inputs
uv run main.py setup
hermes chat --query-file prompt.md
hermes chat --query-file plan.md
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
| prompt.md | 검토 대상 점검 지시문 |
| plan.md | 조치 계획 지시문 |
| expected/review-corrections/ | 저자가 편집한 비교용 수정본·질문 기록 |
| check.py | 원본 보존·점검 결과 저장 확인 |
| main.py | 단계 setup / json / list. 인자 없이 실행하면 할 일과 단계를 안내 |
