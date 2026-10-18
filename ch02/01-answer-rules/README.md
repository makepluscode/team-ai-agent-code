# 01-answer-rules: 에이전트 답변 규칙 적용하기

말투·불확실성 표시·답변 구성의 규칙을 SOUL.md에 더하고, 원본에 없는 수치를 묻는 질문으로 적용 전후를 비교하는 예제입니다. 책 2.1절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch02 ~/agent-work/ch02
cd ~/agent-work/ch02/01-answer-rules
hermes chat --query-file question.md      # 적용 전 답 확인
hermes chat --query-file prompt.md        # 규칙 초안 작성 → 확인 → output/SOUL.md 저장 승인
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak
cp output/SOUL.md ~/.hermes/SOUL.md
hermes chat --query-file question.md      # 적용 후 답 확인
```

- SOUL.md를 저장할 때 헤르메스가 Dangerous Command 상자로 승인을 묻습니다. 저장 경로를 확인한 뒤 Allow once를 고릅니다.
- 초안 작성을 건너뛰려면 output/SOUL.md 대신 이 폴더의 SOUL.md(저자가 편집한 규칙)를 복사합니다.
- 되돌리려면 `cp ~/.hermes/SOUL.md.bak ~/.hermes/SOUL.md`를 실행합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| my-rules.md | 내 답변 규칙 메모(초안의 재료) |
| prompt.md | 메모와 현재 SOUL.md로 규칙 초안을 만드는 지시문 |
| question.md | 원본에 없는 수치를 묻는 확인 질문 |
| input/DOC-001_onboarding.md | 확인 질문이 읽는 온보딩 자료(합성 자료) |
| SOUL.md | 저자가 편집한 이름+답변 규칙. 비교·대체용 |

규칙의 효과는 한 번의 답보다 [확인 필요] 표시, 사실별 출처, '제안:' 구분 같은 형식이 매번 유지되는지로 봅니다. SOUL.md는 모델에 전달하는 규칙이며 파일 쓰기나 외부 전송을 막는 권한 설정이 아닙니다.
