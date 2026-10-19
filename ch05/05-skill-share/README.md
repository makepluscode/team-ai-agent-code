# 05-skill-share: 공유 스킬 배포

3장의 주간 보고 스킬을 팀 위키 저장소의 skills/로 공유하기 전에 점검하는 예제입니다. 점검한 스킬을 저장소에 올리면 동료가
tap으로 설치합니다. 책 5.5절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch05/05-skill-share
hermes chat --query-file prompt.md
uv run check.py
mkdir -p ~/studio-merry-wiki/skills && cp -r output/skills/weekly-report ~/studio-merry-wiki/skills/
hermes skills install <내 GitHub 계정>/studio-merry-wiki/skills/weekly-report
uv run main.py doctor
hermes skills check
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| skills/weekly-report/SKILL.md | 3장에서 만든 주간 보고 스킬 |
| prompt.md | 공유 전 점검 지시문 |
| check.py | 원본 보존·점검 결과 저장 확인 |
| main.py | 단계 doctor. 인자 없이 실행하면 할 일과 단계를 안내 |


v1.7 주간 보고 스킬을 동료 환경에서 tap으로 설치해 같은 결과를 얻는 전 과정은 TODO(검증)입니다.
