# 복사용 명령 모음

『팀 AI 에이전트 실전』 1부(이 책 사용 설명서·1~3장)의 명령과 대화창 지시문을 책에 나오는 순서대로 모았습니다.
책의 줄 앞 `$`·`PS>` 표시는 지웠으므로 상자 안의 내용을 그대로 복사해 터미널에 붙여 넣습니다
(우분투 터미널 Ctrl+Shift+V, 맥 터미널 앱 Cmd+V). 파일로 보내는 지시문은 각 예제 폴더의 .md 파일에 있습니다.

이 파일은 원고에서 자동으로 만듭니다(책 저장소 scripts/make_commands_md.py). 직접 고치지 않습니다.

---

# 이 책 사용 설명서

## 윈도우에서 우분투 설치

줄 앞의 PS>는 프롬프트 표시이므로 입력하지 않습니다.

```powershell
wsl --install
```

다음 명령으로 목록과 버전 열(VERSION)을 확인합니다.

```powershell
wsl -l -v
```

목록에 Ubuntu가 없으면 다음 명령을 실행합니다.

```powershell
wsl --install -d Ubuntu
```


## 헤르메스와 uv 설치

줄 앞의 $는 입력하지 않습니다.

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

헤르메스 설치 프로그램도 uv를 내려받지만 헤르메스 전용 폴더에 두므로, 터미널에서 쓸 uv는 공식 설치 명령으로 따로 설치합니다(uv 설치 안내 https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

업데이트를 확인하느라 십여 초 걸리므로 다음 $가 나올 때까지 기다립니다.

```bash
hermes --version
```

uv와 uv가 실행할 파이썬의 버전을 확인합니다.

```bash
uv --version
uv run python --version
```


## 맥에서 헤르메스 설치

다음 명령을 실행합니다.

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```


## 예제 다운로드

git --version에서 버전이 나오지 않으면 윈도우에서는 sudo apt install -y git으로 먼저 설치합니다.

```bash
mkdir -p ~/team-ai-agent && cd ~/team-ai-agent
git clone https://github.com/makepluscode/team-ai-agent-code.git code
```

헤르메스의 결과는 예제 폴더의 output/에 저장됩니다.

```bash
ls ~/team-ai-agent/code
```


## 파일 열기·편집·옮기기

끝의 마침표(.)는 '지금 폴더'라는 뜻입니다.

```bash
cd ~/team-ai-agent/code
explorer.exe .
```


## 클로드 연결

모델별 비용은 공식 요금표(https://platform.claude.com/docs/en/about-claude/pricing)에서 확인합니다.

```bash
hermes model
```

처음 실행할 때 사용 통계 수집 동의를 묻는 질문이 나오면 읽고 선택합니다.

```bash
cd ~/team-ai-agent/code/ch01/01-hello-jarvis
hermes chat
```


---

# 1부 내 업무에 에이전트 쓰기

## 1.2.1 준비 확인

다음 두 명령으로 준비 상태를 확인합니다.

```bash
hermes --version
ls ~/team-ai-agent/code
```


## 1.2.2 SOUL.md로 이름 붙이기

맥의 터미널 앱에서는 둘째 줄의 백업 명령을 cp -n ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig로 입력합니다(이 책 사용 설명서 [표 0.2]).

```bash
cd ~/team-ai-agent/code/ch01/01-hello-jarvis
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig
cp SOUL.md ~/.hermes/SOUL.md
```

대화창을 열고 위 질문을 입력합니다.

```bash
hermes chat
```

**선택**: 처음 상태로 돌리려면 다음 명령을 실행합니다.

```bash
cp ~/.hermes/SOUL.md.orig ~/.hermes/SOUL.md
```


## 1.3 안내문 점검

파일의 내용이 첫 요청으로 들어가고 대화창이 열린 채 남으므로, 결과를 보고 이어서 고쳐 달라고 말할 수 있습니다.

```bash
cd ~/team-ai-agent/code/ch01/02-notice-check
hermes chat --query-file prompt.md
```

화면의 답이 아니라 파일에 남은 내용이 결과입니다.

```bash
head output/notice-check.md
```


## 1.4 에이전트의 기억

예제 폴더가 아닌 홈 폴더에서 대화창을 엽니다.

```bash
cd ~
hermes chat
```

대화창에 입력:

```text
너는 누구야? 그리고 어제 점검한 예제 폴더는 어디에 있어?
```


## 1.4.1 기억 저장

예제 폴더로 이동해 실행합니다.

```bash
cd ~/team-ai-agent/code/ch01/01-hello-jarvis
hermes chat --query-file remember.md
```

모델이 '기억했습니다'라고 답만 하고 파일에는 쓰지 않는 경우가 있으므로, 저장 여부는 답이 아니라 파일로 확인합니다.

```bash
head ~/.hermes/memories/USER.md ~/.hermes/memories/MEMORY.md
```


## 1.4.2 기억 확인

같은 예제 폴더에서 새 대화로 실행합니다.

```bash
hermes chat --query-file recall.md
```


## 1.4.3 기억에서 뺄 내용

예제 폴더에서 실행합니다.

```bash
cd ~/team-ai-agent/code/ch01/01-hello-jarvis
hermes chat --query-file forget.md
```

헤르메스가 지운 뒤 남은 기억을 보여 주면 /exit로 나와 파일 전체를 다시 열어 확인합니다.

```bash
cat ~/.hermes/memories/USER.md ~/.hermes/memories/MEMORY.md
```


---

# 2장 답변 규칙과 자료 정리

## 2.1.1 말투와 불확실성 표시 기준

예제 폴더로 이동해 이 질문을 지시문 파일(question.md)로 실행합니다.

```bash
cd ~/team-ai-agent/code/ch02/01-answer-rules
hermes chat --query-file question.md
```

예제 폴더에서 지시문 파일로 실행합니다.

```bash
cd ~/team-ai-agent/code/ch02/01-answer-rules
hermes chat --query-file prompt.md
```

저장한 초안을 열어 이름·작성 표시가 그대로인지, 네 부분이 모두 있는지 확인합니다.

```bash
cat output/SOUL.md
```

표현이 달라도 네 부분의 뜻이 같으면 됩니다.

```bash
diff output/SOUL.md SOUL.md
```

맥에서는 첫 줄의 cp --update=none을 cp -n으로 바꿔 입력합니다.

```bash
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak
cp output/SOUL.md ~/.hermes/SOUL.md
```

**선택**: 내 초안 대신 예제의 SOUL.md를 쓰려면 두 번째 줄 대신 다음 명령을 실행합니다.

```bash
cp SOUL.md ~/.hermes/SOUL.md
```


## 2.1.2 규칙 적용 전후 응답 비교

규칙을 적용했으니 같은 폴더에서 같은 질문을 다시 보냅니다.

```bash
hermes chat --query-file question.md
```


## 2.2 원본 보존 정리

파일로 실행할 때는 다음 명령을 씁니다.

```bash
cd ~/team-ai-agent/code/ch02/02-organize-notes
hermes chat --query-file prompt.md
```

헤르메스가 복사와 대응표 저장을 마치면 /exit로 나와 check.py를 실행합니다.

```bash
uv run check.py
```


## 2.3 자료 요약과 비교

파일로 실행할 때는 다음 명령을 씁니다.

```bash
cd ~/team-ai-agent/code/ch02/03-compare-meetings
hermes chat --query-file prompt.md
```

헤르메스가 비교표를 저장하고 다시 읽어 보여 주면 /exit로 대화를 마치고 저장된 파일의 표 부분을 직접 엽니다.

```bash
tail -n 13 output/DOC-006_comparison.md
```


---

# 3장 반복 업무와 내 스킬

## 3.1 주간 보고

예제 폴더로 이동해 이 지시문을 파일(prompt.md)로 실행합니다.

```bash
cd ~/team-ai-agent/code/ch03/01-weekly-report
hermes chat --query-file prompt.md
```

헤르메스가 결과를 저장하면 /exit로 대화를 마치고 같은 폴더에서 저장된 보고의 앞부분을 엽니다.

```bash
head -n 22 output/DOC-009_weekly-report.r1.md
```


## 3.2 주간 보고 스킬

예제 폴더로 이동해 이 지시문을 파일(make-skill.md)로 실행합니다.

```bash
cd ~/team-ai-agent/code/ch03/02-weekly-skill
hermes chat --query-file make-skill.md
```

초안 작성을 건너뛰려면 cp 명령의 원본 경로를 skills/weekly-report/SKILL.md로 바꿔 제공 스킬을 그대로 등록합니다.

```bash
mkdir -p ~/.hermes/skills/weekly-report
cp output/skills/weekly-report/SKILL.md ~/.hermes/skills/weekly-report/SKILL.md
hermes skills list
```

헤르메스가 보고를 저장하고 보여 주면 /exit로 나와 확인합니다.

```bash
cd ~/team-ai-agent/code/ch03/02-weekly-skill
hermes chat
```

같은 폴더에서 -s 옵션으로 weekly-report 스킬을 지정하고 이 지시문 파일(prompt.md)을 실행합니다.

```bash
hermes chat -s weekly-report --query-file prompt.md
```


## 3.3 개인 예약

"$PWD"는 지금 있는 폴더이고, "$(cat prompt.md)"는 prompt.md의 내용을 그대로 넣으라는 뜻입니다.

```bash
cd ~/team-ai-agent/code/ch03/03-weekly-schedule
hermes cron create "0 17 * * 5" --name weekly-report-practice --skill weekly-report --workdir "$PWD" "$(cat prompt.md)"
hermes cron list
```

처음에는 폴더가 없다는 메시지가 나올 수 있습니다.

```bash
ls output/scheduled
hermes cron run weekly-report-practice
ls output/scheduled
head -n 5 output/scheduled/*_DOC-009_weekly-report.r1.md
```

게이트웨이가 실행 중인지는 다음 명령으로 확인합니다.

```bash
hermes cron status
```


## 3.3.2 예약 중지와 수동 실행 복구

예약을 다시 쓰지 않을 때는 remove로 삭제합니다.

```bash
hermes cron pause weekly-report-practice
hermes cron list
hermes cron remove weekly-report-practice
hermes cron list
```


---

# 본문 문장 안의 명령과 맥에서 바꿔 입력하는 명령

본문 문장 안에 나오는 명령과, 맥의 터미널 앱에서 다르게 입력하는 명령입니다.

## 윈도우: git이 없을 때(예제 다운로드 전)

```bash
sudo apt install -y git
```

## 다시 하기(모든 장의 예제 폴더에서)

```bash
uv run reset.py
```

## 2장: 받은 원본(input/)을 처음 내용으로 되돌릴 때(02-organize-notes 폴더에서)

```bash
git restore input
```

## 맥: 1.2.2절 기본 SOUL.md 백업(본문의 cp --update=none 대신)

```bash
cp -n ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig
```

## 맥: 2.1.1절 답변 규칙 적용 전 백업(본문의 cp --update=none 대신)

```bash
cp -n ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak
```

## 맥: 지금 폴더를 Finder로 열기(윈도우의 explorer.exe . 대신)

```bash
open .
```

## 맥: uv 설치

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
