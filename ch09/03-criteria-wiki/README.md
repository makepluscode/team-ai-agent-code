# 03-criteria-wiki: 판단 기준의 위키 반영

검토 6사례에서 확인한 기준을 헤르메스가 DOC-013@r1로 정리하고, raw/에 등록한 뒤 wiki-curator로 판단 기준 페이지(wiki/criteria/review.md)를
만듭니다. 다음 판정과 검토는 이 페이지를 근거로 씁니다. 책 9.4절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch09/03-criteria-wiki
hermes chat --query-file prompt.md
uv run main.py register
hermes chat --query-file wiki.md
uv run main.py preview
uv run main.py apply
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
| wiki/ | 6장까지 정리한 위키 |
| prompt.md | 기준 문서 작성 지시문 |
| wiki.md | 위키 반영 지시문 |
| expected/wiki/criteria/ | 비교용 기준 페이지 |
| check.py | 원본 보존·등록·페이지 저장 확인 |
| main.py | 단계 register / preview / apply. 인자 없이 실행하면 할 일과 단계를 안내 |
