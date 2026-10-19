# 03-weekly-skill: 주간 보고 절차를 내 스킬로 만들기

3.2절에서 확인한 주간 보고 절차를 헤르메스 스킬 weekly-report 하나로 저장하고, 짧은 요청으로 다시 실행하는 예제입니다. 책 3.3절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch03/03-weekly-skill
hermes chat --query-file make-skill.md
mkdir -p ~/.hermes/skills/weekly-report
cp output/skills/weekly-report/SKILL.md ~/.hermes/skills/weekly-report/SKILL.md
hermes skills list
hermes chat                                   # 대화창에 slash.md의 한 줄(/weekly-report …)을 입력
hermes chat -s weekly-report --query-file prompt.md   # 또는 -s로 미리 불러와 파일로 실행
uv run check.py
```

1. make-skill.md로 헤르메스가 SKILL.md 초안을 보여 주면 내용을 확인하고 저장하게 한 뒤 `/exit`로 마칩니다.
2. 초안 작성을 건너뛰려면 `cp`의 원본을 `skills/weekly-report/SKILL.md`(저자가 편집한 스킬)로 바꿉니다.
3. `hermes skills list`에 weekly-report가 local로 나오면 등록된 것입니다.
4. 스킬은 대화창에서 `/weekly-report 요청`을 직접 입력해 부르거나(slash.md의 한 줄) `-s weekly-report`로 미리 불러와 prompt.md를 보냅니다. 슬래시 줄을 `--query-file`로 넘기는 방식은 검증하지 않았습니다. 둘 중 하나만 실행하면 되며 결과 파일 이름이 같습니다. 실행 뒤 `/exit`로 마치고 check.py로 확인합니다.

이미 같은 이름의 스킬(예: 앞 실습의 weekly-report)이 ~/.hermes/skills/에 있으면 덮어씁니다. 덮어쓰기 전에 기존 파일을 다른 이름으로 복사해 두고, 두 파일이 다르면 어느 쪽을 쓸지 먼저 정합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| make-skill.md | SKILL.md 초안을 쓰게 하는 지시문 |
| slash.md | 대화창에 입력할 /weekly-report 한 줄 요청 |
| prompt.md | -s weekly-report와 함께 보내는 짧은 요청 |
| skills/weekly-report/SKILL.md | 저자가 편집한 비교용 스킬(초안 작성을 건너뛸 때 등록) |
| input/ | 3.2절과 같은 회의 노트·업무 노트 정리본, 입력 묶음, 관측 기준 |
| expected/DOC-009_weekly-report.r1.md | 비교용 주간 보고 |
| check.py | 원본 보존과 결과 저장을 확인하고 사람이 대조할 줄을 보여 줍니다 |
