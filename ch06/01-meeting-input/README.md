# 01-meeting-input: 회의 입력 자료와 로컬 전사

> 이 예제는 윈도우의 헤르메스 데스크톱 앱으로 실습합니다. 예제는 홈 폴더의 team-ai-agent\code(C:\Users\로그인 이름\team-ai-agent\code)에 받고, 대화창에 넣을 문장은 [복사용 문장 모음](../../COMMANDS.md)에서 복사합니다. main.py·check.py는 예제 저장소의 자동 시험용이며 책의 실습에서는 쓰지 않습니다.

MTG-001 회의의 입력 자료(회의 정보·용어표·기준 전사문)를 점검하고, 음원이 있으면 로컬 Whisper(faster-whisper)로 전사하는
예제입니다. 음원(input/MTG-001_meeting.mp3)은 기준 전사문(DOC-011@r1)의 대본을 AI 음성으로 합성한 72초짜리 연습 자료이며 실제 회의 녹음이 아닙니다.
전사를 하지 못해도 기준 전사문으로 6.3절을 이어 갈 수 있습니다. 책 6.1~6.2절에 대응합니다.

## 실행 방법

1. 헤르메스 앱에서 새 대화를 열고 다음 문장을 보냅니다.

   작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\01-meeting-input야. 이 폴더의 prompt.md를 읽고 그 내용대로 진행해 줘.

2. 헤르메스가 보여 준 원본과 결과를 읽습니다. 위키 쓰기나 공유 전 확인을 요청하면 내용을 확인한 뒤 답합니다.
3. 위키는 옵시디언에서 열어 출처 링크와 현재 조건을 대조합니다. expected/는 비교용 편집 예시입니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/meeting-manifest.json | 회의 ID·음원·해시·대안 전사문 정보 |
| input/glossary.txt | 전사 힌트용 용어표 |
| input/MTG-001_meeting.mp3 | 합성 회의 음원(AI 음성, 72초) |
| input/DOC-011_transcript-fallback.md | 저자가 쓴 기준 전사문(음원의 대본, 구간 시각 포함) |
| prompt.md | 입력 점검 지시문 |
| transcribe.md | 로컬 전사와 기준 전사문 대조 지시문 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


음원이 있을 때만(선택): uv run --extra transcription main.py transcribe <음원 경로>. 결과는 이 폴더의 output/transcript.json이고, 다음 예제(02-meeting-notes)에서는 ../01-meeting-input/output/transcript.json으로 읽습니다. 전사는 CPU·base·int8 구성을 검토 기준으로 둡니다. 실제 음원의 전사와 원음 청취 대조는 두 기준 장비에서 TODO(검증)입니다.

## 다시 하기

남겨 둘 결과는 먼저 다른 폴더에 복사한 뒤, 새 대화에서 '작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\01-meeting-input야. 이 폴더의 reset.py를 실행해 줘.'라고 부탁합니다. 고치거나 지운 파일은 받은 내용으로 되살아나고 output처럼 새로 생긴 파일은 지워집니다.
