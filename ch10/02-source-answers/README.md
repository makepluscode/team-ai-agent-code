# 02-source-answers: 출처가 있는 답변

헤르메스가 질문 16개에 위키와 원본 출처를 붙여 답하고, main.py의 구조화 조회 결과(qa)와 나란히 대조합니다. 근거가 없는 질문은
지어내지 않고 확인 필요로 남깁니다. 책 10.3절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch10/02-source-answers
hermes chat --query-file prompt.md
uv run main.py qa Q14
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| wiki/ | 9장까지 정리한 위키 페이지와 구조화 출처 자료(facts.json) |
| raw/ | 문서 버전별 원본(DOC-001~DOC-013) |
| input/queries.json | 질문 20개와 질문별 기준 시각(as_of) |
| prompt.md | 질문 16개 답변 지시문 |
| check.py | 원본 보존·답변 저장 확인 |
| main.py | 단계 qa / sources. 인자 없이 실행하면 할 일과 단계를 안내 |
