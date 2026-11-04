# 복사용 문장 모음

『팀 AI 에이전트 실전』 앱 버전(이 책 사용 설명서·1~6장)에서 헤르메스 앱 대화창에 넣는 문장을 책에 나오는 순서대로 모았습니다.
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


---

# 2부 자료를 위키로 쌓고 동료와 잇기

## 4.3 정리 규칙

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch04\01-wiki-folder야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 4.4 첫 위키 페이지

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch04\02-first-page야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인. 적용해 줘. 확인한 사람은 매니저야.
```


## 4.5 출처 조회

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch04\03-source-query야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


---

# 5장 동료와 위키로 이어서 일하기

## 5.1.2 첫 공유 준비

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\01-share-repo야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
보여 준 파일 목록을 확인했어. 그 파일만 비공개 저장소에 첫 기록으로 올려 줘. 기존 저장소나 파일을 덮어써야 하면 멈춰 줘.
```


## 5.1.3 동료의 사본 준비

대화창에 입력:

```text
방금 확인한 공유 저장소를 홈 폴더의 studio-merry-wiki-member에 받아 줘. 이 폴더는 송지우 역할의 사본이야. 이미 폴더가 있으면 덮어쓰지 말고 멈춰 줘. 두 폴더의 연결된 저장소 주소와 마지막 변경 이력이 같은지 보여 줘.
```


## 5.2.1 동기화 스킬 준비

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\02-wiki-sync야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 5.2.2 고른 파일만 동기화

대화창에 입력:

```text
작업 폴더는 홈 폴더의 studio-merry-wiki야. wiki-sync 스킬로 동기화해 줘. 바뀐 파일 목록과 제안 기록 문구를 먼저 보여 줘. 내가 고른 파일과 문구를 확인한 뒤에만 기록과 동기화를 진행해 줘. 충돌이나 오류가 나면 멈춰 줘.
```


## 5.2.3 충돌과 중단

대화창에 입력:

```text
동기화는 멈춘 상태로 둬. 충돌한 파일과 양쪽에서 바꾼 내용을 나란히 보여 줘. 원본은 보존하고, 어느 쪽을 남길지는 아직 결정하지 마. 강제로 올리거나 한쪽 변경을 버리지 마.
```


## 5.3.2 전체 변경안 확인

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\03-change-memo야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인. 적용해 줘. 확인한 사람은 매니저야.
```


## 5.4.1 갱신된 위키 받기

대화창에 입력:

```text
홈 폴더의 team-ai-agent\code\ch05\03-change-memo에서 갱신한 위키를 같은 ch05의 04-member-revision으로 받아 쓸 거야. 두 폴더의 AGENTS.md를 먼저 읽고, 옮길 위키 파일과 필요한 출처 원본 목록을 보여 줘. 04의 기존 온보딩 가이드와 다른 원본은 바꾸지 말고, 내가 확인할 때까지 복사하지 마.
```


## 5.4.2 온보딩 가이드의 새 버전

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\04-member-revision야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 5.5.1 개인 설정 점검

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\05-skill-share야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 5.5.2 공유 원본과 설치 사본

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch05\05-skill-share야. 이 폴더의 share.md를 읽고 그 지시대로 해 줘. 팀 위키는 홈 폴더의 studio-merry-wiki야.
```

대화창에 입력:

```text
홈 폴더의 studio-merry-wiki-member에서 공유받은 skills\weekly-report를 읽어 줘. 지금 설치된 weekly-report와 차이, 설치할 위치, 스킬 출처를 보여 줘. 기존 스킬은 아직 바꾸지 마.
```


## 5.5.3 동료의 실행 결과

대화창에 입력:

```text
공유받은 weekly-report 스킬로 주간 보고를 만들어 줘. 입력 자료는 홈 폴더의 team-ai-agent\code\ch05\05-skill-share에 있는 input\DOC-004_weekly-meetings.md와 raw\report-input이야. 관측 기준은 input\snapshot.json에서 읽어 줘. 관측 기준은 파일에 든 값을 쓰고, 보고서는 이 예제의 output 안에 새 이름으로 저장해 줘. 저장한 뒤 관측 완료 건수와 미입력, 업무 상태를 다시 읽어 보여 줘.
```


---

# 6장 회의에서 결정 기록까지

## 6.1 회의 자료

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\01-meeting-input야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```


## 6.3 회의록 초안과 확인

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\02-meeting-notes야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
후속 안내자료의 최종 검토자는 정해지지 않았어. 합성 대본의 해당 발언을 다시 읽고 담당과 기한을 미정으로 고쳐 줘. 온보딩 가이드 수정은 확인 대기를 유지해 줘. 회의록은 아직 초안이며 원음 확인은 미완료라고 적어 줘.
```

대화창에 입력:

```text
제공 합성 대본과 회의록 초안을 대조했어. 대본 근거 확인자는 매니저로 적어 줘. 원음 확인은 미완료로 남기고, 실제 회의의 원음 확인을 마친 기록으로 바꾸지 마. 수정한 파일을 다시 읽어 보여 줘.
```


## 6.4 위키의 현재 결정

대화창에 입력:

```text
앞 절에서 만든 02-meeting-notes\output\DOC-012_meeting-notes.md를 이번 예제의 input\DOC-012_meeting-notes.md와 비교해 줘. 경로는 ch06 폴더 기준이야. 다른 내용을 먼저 보여 주고 내 확인을 기다려 줘. 내가 확인하면 앞 절 결과를 이번 입력으로 복사하되, 제공 입력은 output\input-before에 백업해 줘. 합성 대본 사용과 원음 확인 미완료 표시를 유지해 줘.
```

대화창에 입력:

```text
작업 폴더는 홈 폴더의 team-ai-agent\code\ch06\03-decision-wiki야. 이 폴더의 prompt.md를 읽고 그 지시대로 해 줘. 경로는 모두 작업 폴더 기준이야.
```

대화창에 입력:

```text
확인. 적용해 줘. 확인한 사람은 매니저야. 제공 합성 자료로 한 실습이며 원음 확인은 미완료라는 표시를 유지해 줘.
```
