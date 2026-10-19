# 03-wiki-audit: 모순과 오래된 기록 점검

옛 온보딩 가이드처럼 현재 결정과 어긋나는 문서를 헤르메스가 찾아 보고합니다. 위키와 원본은 고치지 않고 보고서만 남깁니다.
책 10.4절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch10/03-wiki-audit
hermes chat --query-file prompt.md
uv run main.py qa Q17
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| wiki/ | 9장까지 정리한 위키 페이지와 구조화 출처 자료(facts.json) |
| raw/ | 문서 버전별 원본(DOC-001~DOC-013) |
| input/queries.json | 질문 20개와 질문별 기준 시각(as_of) |
| input/qa-fixtures/ | 대조용 옛 문서(현재 사실 아님) |
| prompt.md | 모순 점검 지시문 |
| check.py | 원본 보존·보고서 저장 확인 |
| main.py | 단계 qa / sources. 인자 없이 실행하면 할 일과 단계를 안내 |
