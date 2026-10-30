# 복사용 문장 모음

『팀 AI 에이전트 실전』 1부(이 책 사용 설명서·1~3장)에서 헤르메스 앱 대화창에 넣는 문장을 책에 나오는 순서대로 모았습니다.
상자 안의 내용을 그대로 복사해(Ctrl+C, 맥 Cmd+C) 헤르메스 앱의 입력창에 붙여 넣습니다(Ctrl+V, 맥 Cmd+V).
헤르메스가 읽을 지시문(prompt.md 등)은 각 예제 폴더에 있습니다.

이 파일은 원고에서 자동으로 만듭니다(책 저장소 scripts/make_commands_md.py). 직접 고치지 않습니다.

---

# 이 책 사용 설명서

## 클로드 연결

대화창에 입력:

```text
온보딩 자료를 한 장으로 요약할 때 빠뜨리면 안 되는 확인 항목 세 가지를 짧게 알려 줘.
```


## 예제 받기

대화창에 입력:

```text
https://github.com/makepluscode/team-ai-agent-code 저장소를 내 홈 폴더의 team-ai-agent\code 폴더로 내려받아 줘. 받은 뒤 그 안의 폴더 목록을 보여 줘.
```


## 파일 열기

대화창에 입력:

```text
홈 폴더의 team-ai-agent\code\ch01\02-notice-check\output\notice-check.md를 미리보기 창에 열어 줘.
```


---

# 1부 내 업무에 에이전트 쓰기

## 1.2.2 SOUL.md로 이름 붙이기

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\01-hello-jarvis야. 헤르메스 설정 폴더의 SOUL.md를 이 작업 폴더의 SOUL.md 내용으로 바꿔 줘. 바꾸기 전에 설정 폴더의 SOUL.md를 설정 폴더 안에 SOUL.md.orig로 백업하고, 백업이 이미 있으면 덮어쓰지 마. 작업 폴더의 SOUL.md는 고치지 마.
```

대화창에 입력:

```text
너는 누구야? 한 문장으로 자기소개해 줘.
```


## 1.3 안내문 점검

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\02-notice-check야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 1.4 에이전트의 기억

대화창에 입력:

```text
너는 누구야? 그리고 어제 점검한 예제 폴더는 어디에 있어?
```


## 1.4.1 기억 저장

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\01-hello-jarvis야. 이 폴더의 remember.md를 읽고 그 지시대로 해 줘.
```


## 1.4.2 기억 확인

대화창에 입력:

```text
기억에 있는 '실습용' 항목을 그대로 알려 줘. 그다음 1장 안내문 점검 예제 폴더(02-notice-check)를 찾아서, output\notice-check.md가 있으면 기억한 선호대로 두 문장으로 보고하고 없으면 없다고 말해 줘.
```


## 1.4.3 기억에서 뺄 내용

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch01\01-hello-jarvis야. 이 폴더의 forget.md를 읽고 그 지시대로 해 줘.
```


---

# 2장 답변 규칙과 자료 정리

## 2.1.1 말투와 불확실성 표시 기준

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch02\01-answer-rules야. 이 폴더의 question.md를 읽고 그 질문에 답해 줘.
```

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch02\01-answer-rules야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인. 초안을 output\SOUL.md에 저장하고, 헤르메스 설정 폴더의 SOUL.md(1장에서 자비스로 바꾼 파일)를 같은 폴더에 SOUL.md.bak으로 백업한 뒤(이미 있으면 덮어쓰지 마) 초안으로 바꿔 줘. 예제 폴더의 SOUL.md는 그대로 둬.
```


## 2.1.2 규칙 적용 전후 응답 비교

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch02\01-answer-rules야. 이 폴더의 question.md를 읽고 그 질문에 답해 줘.
```


## 2.2 원본 보존 정리

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch02\02-organize-notes야. 이 폴더의 prompt.md를 읽고 그 지시대로 진행해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인했어. 표대로 정리해 줘. 다 끝나면 원본 12개가 그대로인지와 정리본이 원본과 내용이 같은지 확인하고, 정리 10개·중복 1개·확인 필요 1개인지 세어서 알려 줘.
```


## 2.3 자료 요약과 비교

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch02\03-compare-meetings야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


---

# 3장 반복 업무와 내 스킬

## 3.1 주간 보고

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\01-weekly-report야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 3.2 주간 보고 스킬

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill이야. 이 폴더의 make-skill.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인. 초안을 output\skills\weekly-report\SKILL.md에 저장하고, 이 스킬을 내 헤르메스 스킬로 등록해 줘. 같은 이름의 스킬이 이미 있으면 덮어쓰지 말고 알려 줘.
```

대화창에 입력:

```text
/weekly-report 홈 폴더의 team-ai-agent\code\ch03\02-weekly-skill 폴더의 주간 보고를 그 폴더의 output\DOC-009_weekly-report_skill-run.md에 만들어 줘.
```


## 3.3 개인 예약

대화창에 입력:

```text
매주 금요일 오후 5시에 실행되는 예약을 weekly-report-practice라는 이름으로 등록해 줘. 작업 폴더는 홈 폴더의 team-ai-agent\code\ch03\03-weekly-schedule이고, 예약이 실행할 지시는 그 폴더의 prompt.md 내용 그대로야. 등록한 뒤 예약 목록과 다음 실행 시각을 보여 줘.
```


## 3.3.2 예약 중지와 수동 실행 복구

대화창에 입력:

```text
weekly-report-practice 예약을 삭제하고, 남은 예약 목록을 보여 줘.
```
