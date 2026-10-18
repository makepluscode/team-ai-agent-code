# 01-classify-requests: 요청 분류와 담당 제안

헤르메스가 요청 10건의 유형·긴급도·담당 후보·확인 필요 여부를 판정해 요청별 JSON으로 저장하고, main.py가 스키마·명부·근거(본문 문장)를
검사한 뒤 기록 DB에 남깁니다. 검사를 통과하지 못한 판정은 사람 확인 대상으로 기록됩니다. 책 8.1~8.3절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch08 ~/agent-work/ch08
cd ~/agent-work/ch08/01-classify-requests
uv run main.py setup
hermes chat --query-file prompt.md
hermes chat --query-file routing.md
uv run main.py record
uv run main.py list
hermes chat --query-file status.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/internal-requests.json | 내부 요청 8건(합성) |
| input/members.json | 역할 명부 M01~M05 |
| input/snapshot.json | 독립 시작 시점의 업무·사건 기록 |
| raw/ | 6장까지의 원본(문서 버전별) |
| input/routing-criteria.json | 팀이 정한 유형·긴급도·확인 기준 |
| prompt.md | 분류·담당 제안 지시문 |
| routing.md | 담당 후보 점검 지시문 |
| status.md | 판정 기록 현황(DOC-014@r3) 지시문 |
| main.py | setup / record: 판정 검사·기록 / list / json |
| expected/classification/ | 저자가 편집한 비교용 판정(헤르메스에 주지 않음) |
| check.py | 원본 보존·판정 10건 기록 확인 |
