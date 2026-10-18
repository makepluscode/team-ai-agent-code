# 01-onboarding-guide: 온보딩 가이드 잠정안

온보딩 자료로 새 팀원에게 줄 짧은 가이드(DOC-007 문서 버전 r1)를 만드는 예제입니다. 잠정 일정과 미정 조건을 그대로 남기는지 확인합니다. 책 3.1절에 대응합니다.

## 실행 방법

```bash
cp -r ~/team-ai-agent/code/ch03 ~/agent-work/ch03
cd ~/agent-work/ch03/01-onboarding-guide
hermes chat --query-file prompt.md
uv run check.py
```

헤르메스가 결과를 저장하고 다시 읽어 보여 주면 `/exit`로 대화를 마친 뒤 check.py를 실행합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 가이드 구성과 저장 위치를 담은 지시문 |
| input/DOC-001_onboarding.md | 온보딩 자료 원본(합성 자료) |
| expected/DOC-007_onboarding-guide.r1.md | 저자가 편집한 비교용 결과 |
| check.py | 원본 보존과 결과 저장을 확인하고, 사람이 대조할 줄을 보여 줍니다 |
