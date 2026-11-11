# 02-meeting-notes: 회의 결정과 할 일 추출

> 이 예제는 윈도우의 헤르메스 데스크톱 앱으로 실습합니다. 예제는 홈 폴더의 team-ai-agent\code(C:\Users\로그인 이름\team-ai-agent\code)에 받고, 대화창에 넣을 문장은 [복사용 문장 모음](../../COMMANDS.md)에서 복사합니다. main.py·check.py는 예제 저장소의 자동 시험용이며 책의 실습에서는 쓰지 않습니다.

기준 전사문에서 결정·할 일·취소·미정을 구분한 회의록 초안을 만들고, 사람이 음원의 해당 구간을 들어 대조합니다. 책 6.3절에 대응합니다.

## 실행 방법

1. 헤르메스 앱에서 새 대화를 열고 다음 문장을 보냅니다.

   작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\02-meeting-notes야. 이 폴더의 prompt.md를 읽고 그 내용대로 진행해 줘.

2. 헤르메스가 보여 준 원본과 결과를 읽습니다. 위키 쓰기나 공유 전 확인을 요청하면 내용을 확인한 뒤 답합니다.
3. 위키는 옵시디언에서 열어 출처 링크와 현재 조건을 대조합니다. expected/는 비교용 편집 예시입니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/DOC-011_transcript-fallback.md | 기준 전사문(합성) |
| input/meeting-manifest.json | 회의 정보 |
| wiki/ | 5장까지 갱신된 위키 |
| prompt.md | 회의록 초안 지시문 |
| expected/DOC-012_meeting-notes.md | 비교용 회의록 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


## 다시 하기

남겨 둘 결과는 먼저 다른 폴더에 복사한 뒤, 새 대화에서 '작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\02-meeting-notes야. 이 폴더의 reset.py를 실행해 줘.'라고 부탁합니다. 고치거나 지운 파일은 받은 내용으로 되살아나고 output처럼 새로 생긴 파일은 지워집니다.
