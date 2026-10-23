# 03-mail-input: 추가 입력 경로인 메일

선택 입력인 외부 메일 2건(합성)을 내부 요청과 같은 형식으로 접수해 요청 10건을 만듭니다. Gmail 실제 연결 없이도 8~12장을 진행할 수
있게 제공 메일 자료를 씁니다. 실제 Gmail 연결은 부록 C를 따릅니다. 책 7.4절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch07/03-mail-input
uv run main.py intake
hermes chat --query-file prompt.md
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
| input/optional-mail.json | 제공 메일 2건(합성, REQ-009·010) |
| input/mail/ | 메일 원문(.eml, 합성) |
| prompt.md | 메일 요청 정리 지시문 |
| check.py | 원본 보존·요청 10건 확인 |
| main.py | 단계 intake / json / list. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |
