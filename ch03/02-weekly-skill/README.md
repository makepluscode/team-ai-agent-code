# 02-weekly-skill: 주간 보고 절차를 내 스킬로 만들기

> 이 예제는 윈도우의 헤르메스 데스크톱 앱으로 실습합니다. 예제는 홈 폴더의 team-ai-agent\code(C:\Users\로그인 이름\team-ai-agent\code)에 받고, 대화창에 넣을 문장은 [복사용 문장 모음](../../COMMANDS.md)에서 복사합니다. 헤르메스 설정 폴더는 C:\Users\로그인 이름\AppData\Local\hermes입니다.

3.1절에서 확인한 주간 보고 절차를 헤르메스 스킬 weekly-report 하나로 저장하고, 짧은 요청으로 다시 실행하는 예제입니다. 책 3.2절에 대응합니다.

## 실행 방법

1. 스킬 초안: 새 대화에서 다음 문장을 보내고, 초안을 읽은 뒤 이어지는 '확인' 문장으로 답합니다.

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill이야. 이 폴더의 make-skill.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

```text
확인. 초안을 output\skills\weekly-report\SKILL.md에 저장하고, 이 스킬을 내 헤르메스 스킬로 등록해 줘. 같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 알려 줘.
```

2. 등록 확인: 헤르메스가 설정 폴더의 skills\weekly-report\SKILL.md에 등록하면 앱 왼쪽 [Capabilities]의 스킬 목록에 weekly-report가 보입니다.
3. 스킬 실행: 새 대화의 입력창에 slash.md의 한 줄과 같은 다음 문장을 붙여 넣습니다(/를 치면 자동 완성 목록이 나옵니다).

```text
/weekly-report 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill 폴더의 주간 보고를 그 폴더의 output\DOC-009_weekly-report_skill-run.md에 만들어 줘.
```

- 초안 작성을 건너뛰려면 1번 대신 '작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill이야. 이 폴더의 skills\weekly-report\SKILL.md를 내 헤르메스 스킬로 등록해 줘. 같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 알려 줘.'라고 부탁합니다.
- 같은 이름의 스킬이 이미 있다는 답이 나오면 기존 스킬을 쓸지 바꿀지 먼저 정합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| make-skill.md | SKILL.md 초안을 쓰게 하는 지시문 |
| slash.md | 대화창에 입력할 /weekly-report 한 줄 요청 |
| prompt.md | 스킬 이름으로 부르는 짧은 요청(슬래시 대신 쓸 때) |
| skills\weekly-report\SKILL.md | 편집한 비교용 스킬(초안 작성을 건너뛸 때 등록) |
| input\ | 3.1절과 같은 회의 노트·업무 노트 정리본, 입력 묶음, 관측 기준 |
| expected\DOC-009_weekly-report.r1.md | 비교용 주간 보고 |
| reset.py | 결과 폴더(output\)를 지우는 스크립트. 앱에서는 '다시 하기'처럼 대화로 지웁니다 |

## 확인할 것

결과 파일을 열어 원본(input\)과 대조합니다.

- 관측 기준 시각이 input\snapshot.json의 값 그대로인가
- 완료가 항목키 ITEM-001~004의 네 건이고, 대화의 재언급을 다시 세지 않았는가
- ITEM-005·006이 완료가 아니라 제안·상태 미기재로 남았는가
- 보고 업무 TASK-001이 '확인 대기'인가

## 다시 하기

새 대화에서 다음처럼 부탁합니다. 받은 원본(input\)과 헤르메스 설정 폴더는 지우지 않습니다. 등록한 스킬은 설정 폴더에 남습니다.

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill이야. output 폴더의 파일 목록을 보여 주고, 내가 확인하면 지워 줘.
```
