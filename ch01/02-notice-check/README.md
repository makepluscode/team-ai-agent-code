# 02-notice-check: 안내문의 자료 경로 확인

> 이 예제는 윈도우의 헤르메스 데스크톱 앱으로 실습합니다. 예제는 홈 폴더의 team-ai-agent\code(C:\Users\로그인 이름\team-ai-agent\code)에 받고, 대화창에 넣을 문장은 [복사용 문장 모음](../../COMMANDS.md)에서 복사합니다. 헤르메스 설정 폴더는 C:\Users\로그인 이름\AppData\Local\hermes입니다.

매니저가 새 팀원에게 보낼 안내문(input\notice.md)에 적힌 자료 경로 세 개가 팀 자료함(input\shared\)에 실제로 있는지 헤르메스가 하나씩 열어 확인하고, 결과를 표로 저장하는 예제입니다. 내 폴더를 볼 수 없는 보통의 챗봇은 할 수 없고, 파일 도구를 쓰는 에이전트는 할 수 있는 일입니다. 책 1.3절에 대응합니다.

## 실행 방법

새 대화에서 다음 문장을 보냅니다.

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\02-notice-check야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

헤르메스가 결과를 저장하고 다시 읽어 보여 주면, 'output\notice-check.md를 미리보기 창에 열어 줘.'라고 부탁하거나 파일 탐색기에서 메모장으로 열어 저장된 파일을 확인합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 헤르메스에 보내는 지시문 |
| input\notice.md | 매니저의 안내문 초안(합성 자료). 경로 세 개 가운데 하나가 실제 위치와 다릅니다 |
| input\shared\ | 팀 자료함 사본. 파일 세 개(team\, tools\, archive\) |
| output\ | 헤르메스가 결과를 저장하는 곳(실행하면 생깁니다) |
| expected\notice-check.md | 편집한 비교용 결과. 실제 모델 응답이 아닙니다 |
| reset.py | 결과 폴더(output\)를 지우는 스크립트. 앱에서는 '다시 하기'처럼 대화로 지웁니다 |

3번 경로만 '위치 다름'(실제 위치 shared/archive/notice-retro.md)이고 나머지 두 개는 '정상'이면 됩니다.

## 다시 하기

새 대화에서 다음처럼 부탁합니다. 받은 원본(input\)과 헤르메스 설정 폴더는 지우지 않습니다.

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\02-notice-check야. output 폴더의 파일 목록을 보여 주고, 내가 확인하면 지워 줘.
```
