# 02-onboarding-plan: 온보딩 자료로 첫 계획 만들기

매니저의 온보딩 자료(DOC-001)를 헤르메스가 읽고, 새 팀원용 가이드와 첫 일정이 담긴 온보딩 계획(DOC-005)을 저장한 뒤 다시 읽어 보여 주는 예제입니다. 책 1.6절에 대응합니다.

## 실행 방법

```bash
mkdir -p ~/agent-work
cp -r --update=none ~/team-ai-agent/code/ch01 ~/agent-work/
cd ~/agent-work/ch01/02-onboarding-plan
hermes chat --query-file prompt.md
uv run check.py
```

`hermes chat --query-file`은 prompt.md를 첫 요청으로 보내고 대화를 이어 갑니다. 결과를 확인한 뒤 `/exit`로 나옵니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 헤르메스에 보내는 지시문 |
| input/DOC-001_onboarding.md | 온보딩 자료 원본(합성 자료). 수정하지 않습니다 |
| output/ | 헤르메스가 결과를 저장하는 곳(실행하면 생깁니다) |
| expected/DOC-005_onboarding-plan.md | 저자가 편집한 비교용 결과. 실제 모델 응답이 아닙니다 |
| check.py | 원본 보존과 결과 저장을 확인하고, 사람이 대조할 줄을 보여 줍니다 |

## 다시 하기

기존 사본은 그대로 두고 새 이름으로 다시 복사합니다.

```bash
cp -r ~/team-ai-agent/code/ch01 ~/agent-work/ch01-retry
```
