# 01-revision-search: 문서 버전 관리와 위키 검색

9장까지 쌓인 문서 버전과 위키를 헤르메스가 정리하고(prompt.md), 질문 20개의 근거 위치를 먼저 찾습니다(search.md). main.py는
facts.json의 구조화 출처로 같은 질문의 근거를 확인합니다. 책 10.1~10.2절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch10 ~/agent-work/ch10
cd ~/agent-work/ch10/01-revision-search
hermes chat --query-file prompt.md
hermes chat --query-file search.md
uv run main.py check
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| wiki/ | 9장까지 정리한 위키 페이지와 구조화 출처 자료(facts.json) |
| raw/ | 문서 버전별 원본(DOC-001~DOC-013) |
| input/queries.json | 질문 20개와 질문별 기준 시각(as_of) |
| prompt.md | 문서 버전 정리 지시문 |
| search.md | 근거 위치 검색 지시문 |
| main.py | check: 질문 20개 구조화 조회 점검 / qa: 질문 하나 조회 |
| check.py | 원본 보존·결과 저장 확인 |
