# 2장 설치와 팀 위키 받기

『팀 AI 에이전트 실전』 2장의 실습 안내입니다. 이 문서만 보고 처음부터 끝까지 따라 할 수 있게 썼습니다. 윈도우(WSL2) 기준이며, 맥은 도서 부록 A를 함께 봅니다.

- 원고: `content/ch02_setup_v0.md`(도서 저장소)
- 결과물: 대화와 파일 작업이 되고, 팀 위키 저장소를 받아 둔 헤르메스
- 소요 시간: 1~2시간(WSL2를 처음 설치하면 재시작 포함)
- 이 폴더의 자료
  - [wiki-starter/](wiki-starter/) — 팀 위키 시작 저장소(규칙 파일, 첫 메모, 위키 동기화 스킬)
  - [tests/](tests/) — 위키 동기화 실행 파일 시험(확장 노트용)

> 확인 범위: 위키 동기화 실행 파일은 로컬 Git 저장소로 시험했습니다(`tests/`, 2026-10-14). 헤르메스 설치·모델 호출·GitHub 비공개 저장소 연결은 기준 장비에서 아직 확인하지 않았습니다. 화면이나 메시지가 이 문서와 다르면 공식 문서를 우선합니다.

## 진행 순서와 완료 기준

| 단계 | 할 일 | 실행하는 창 | 완료 기준 |
|---|---|---|---|
| 1 | WSL2와 Ubuntu 준비 | PowerShell(관리자) | `wsl -l -v`에 Ubuntu, VERSION 2 |
| 2 | 헤르메스 설치 | Ubuntu | `hermes --version`, `python3 --version`이 출력됨 |
| 3 | 상용 AI 연결 | Ubuntu | 짧은 질문에 응답이 옴 |
| 4 | GitHub 연결, 예제 저장소와 팀 위키 받기 | Ubuntu | 홈 폴더에 `team-ai-agent-code`와 `studio-merry-wiki`가 있음 |
| 5 | 첫 파일 작업 | Ubuntu | `work/output/first-file.md`가 생기고 검사가 통과함 |

명령마다 **어느 창**에서 실행하는지 적었습니다. PowerShell 명령을 Ubuntu에, Ubuntu 명령을 PowerShell에 넣으면 설치와 상관없는 오류가 납니다.

팀에서 할 일이 다릅니다. **위키 담당자**(스튜디오 메리는 PM) 한 명이 4단계에서 팀 위키 저장소를 만들고 팀원을 초대합니다. **다른 팀원**은 초대를 수락한 뒤 받기만 합니다. 혼자 연습한다면 담당자 역할로 진행합니다.

---

## 1단계. WSL2와 Ubuntu 준비

**PowerShell(관리자 권한)** 에서 실행합니다. 시작 메뉴에서 PowerShell을 오른쪽 클릭해 '관리자 권한으로 실행'을 고릅니다.

```powershell
wsl --install
```

설치가 끝나면 컴퓨터를 다시 시작합니다. 최신 WSL(2026-10-15 기준 WSL 3.0.3)은 이 명령으로 WSL만 설치하고 Ubuntu는 설치하지 않습니다. 다시 시작한 뒤 PowerShell을 열고 Ubuntu를 설치합니다.

```powershell
wsl --install -d Ubuntu
```

Ubuntu를 내려받은 뒤 사용자 이름과 비밀번호를 정하라고 합니다. 이 비밀번호는 뒤에서 `sudo` 명령을 쓸 때 다시 입력합니다. 이어서 Ubuntu 지표 수집에 동의할지 묻는데(Y/n), 실습과 관계없으므로 원하는 대로 답합니다.

다시 PowerShell에서 확인합니다.

```powershell
wsl -l -v
```

목록에 `Ubuntu`가 있고 `VERSION`이 `2`이면 완료입니다. 이후 명령은 모두 **Ubuntu 창**(시작 메뉴의 Ubuntu 또는 Windows Terminal의 Ubuntu 탭)에서 실행합니다.

- 공식 안내: https://learn.microsoft.com/windows/wsl/install
- 헤르메스의 WSL2 안내: https://hermes-agent.nousresearch.com/docs/user-guide/windows-wsl-quickstart
- 막히면: 회사 PC에서 가상화가 꺼져 있거나 설치 권한이 없을 수 있습니다. 전산 담당자에게 'WSL2 사용 가능 여부'를 확인합니다.

## 2단계. 헤르메스 설치

**Ubuntu** 에서 공식 설치 명령을 실행합니다.

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

설치기는 끝나면 설정 마법사(Quick Setup·Full setup·Blank Slate)를 바로 띄웁니다. 이 책은 모델을 3단계의 `hermes model`로 연결하므로 Esc로 닫습니다. 이어서 게이트웨이를 서비스로 시작할지, 로그인할 때 자동으로 시작할지 두 번 묻습니다. 예약은 3장에서 다루므로 두 번 모두 `n`으로 답합니다.

설치가 끝나면 Ubuntu 창을 닫았다가 다시 열고(또는 `source ~/.bashrc`) 확인합니다. `hermes --version`은 처음에 업데이트를 확인하느라 15초가량 걸릴 수 있습니다.

```bash
hermes --version
python3 --version
```

두 명령 모두 버전이 출력되면 완료입니다. 실습 패키지의 제공 코드는 Python 3.10 이상에서 동작합니다.

| 증상 | 원인 | 할 일 |
|---|---|---|
| `hermes: command not found` | 창을 다시 열지 않음(PATH) | Ubuntu 창을 닫고 다시 엶 |
| 내려받기 실패 | 네트워크·회사 방화벽 | 다른 네트워크에서 시도하거나 전산 담당자에게 확인 |

- 공식 설치 문서: https://hermes-agent.nousresearch.com/docs/getting-started/installation

## 3단계. 상용 AI 연결

이 책은 클로드를 기준으로 합니다. Anthropic 콘솔(https://console.anthropic.com)에서 API 키를 발급합니다. 키는 한 번만 보이므로 바로 다음 명령에서 입력합니다.

```bash
hermes model
```

제공자 목록에서 Anthropic을 고르고, 키를 입력하고, 모델을 고릅니다(공식 안내 https://hermes-agent.nousresearch.com/docs/getting-started/quickstart). OpenAI나 제미나이를 쓰면 같은 화면에서 제공자만 바꿉니다.

연결을 확인합니다. 파일을 읽거나 바꾸지 않는 짧은 질문으로 합니다.

```bash
hermes chat
```

대화창에 다음을 입력합니다.

```text
마케팅 대행사에서 고객 요청을 정리할 때 확인할 항목을 세 가지로 적어 줘.
```

응답이 오면 완료입니다. 대화를 끝내려면 `/exit`를 입력하거나 Ctrl+C를 누릅니다.

- **API 키는 자기 컴퓨터에만 둡니다.** 팀 위키나 메신저에 붙여 넣지 않습니다.
- 응답이 오지 않으면 오류 메시지를 보고 구분합니다: 잘못된 키 / 사용할 수 없는 모델 / 결제 미등록·사용 한도 / 네트워크.

## 4단계. GitHub 연결, 예제 저장소와 팀 위키 받기

GitHub 계정이 필요합니다. 없으면 도서 부록 B를 따라 먼저 가입합니다(https://github.com/signup).

### 4-1. gh 설치와 로그인 (모두)

GitHub 공식 명령줄 도구 gh를 설치합니다. **Ubuntu** 에서 공식 안내(https://github.com/cli/cli/blob/trunk/docs/install_linux.md)의 명령을 그대로 실행합니다. 중간에 Ubuntu 비밀번호를 묻습니다.

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

로그인하고, Git이 GitHub에 올릴 때 이 로그인을 쓰도록 설정하고, 작성자 이름을 정합니다. 작성자 이름은 위키의 변경 기록에 '누가 바꿨는지'로 남습니다.

```bash
gh auth login
gh auth setup-git
git config --global user.name "<이름>"
git config --global user.email "<메일>"
```

`gh auth login`에서는 GitHub.com → HTTPS → 브라우저 로그인을 고릅니다. 화면에 나온 코드를 브라우저에 입력하면 연결됩니다. WSL에서 브라우저가 자동으로 열리지 않으면 표시된 주소를 윈도우 브라우저에 직접 붙여 넣습니다. 확인은 다음 명령으로 합니다.

```bash
gh auth status
```

### 4-2. 책의 예제 저장소 받기 (모두)

```bash
cd ~
gh repo clone makepluscode/team-ai-agent-code
```

홈 폴더에 `team-ai-agent-code`가 생기면 완료입니다. 이 문서도 그 안의 `ch02/README.md`입니다.

> TODO(검증): 출간 시 예제 저장소의 공개 여부와 주소를 확정합니다.

### 4-3. 팀 위키 저장소 만들기 (위키 담당자만)

예제 저장소의 [wiki-starter](wiki-starter/)를 복사해 팀의 **비공개** 저장소를 만듭니다.

**만들어 보기** — 헤르메스에게 맡깁니다. Ubuntu에서 `hermes chat`을 열고 다음을 붙여 넣습니다.

```text
팀 위키 저장소를 준비해 줘.

먼저 gh auth status로 GitHub 로그인 상태를 확인하고,
로그인돼 있지 않으면 내가 gh auth login을 직접 실행하도록 알려 줘.

로그인이 확인되면 ~/team-ai-agent-code/ch02/wiki-starter 폴더의 내용을
~/studio-merry-wiki 로 복사하고, 그 폴더를 Git 저장소로 만들어 첫 기록을 남긴 뒤
비공개 GitHub 저장소 studio-merry-wiki로 올려 줘.
실행할 명령을 먼저 보여 주고, 내가 확인한 뒤 실행해 줘.

끝나면 폴더 목록과 .gitignore 내용을 보여 주고,
API 키나 녹음 파일이 올라가지 않게 돼 있는지 확인해 줘.
Git 작성자 이름과 메일이 설정돼 있는지도 확인해 줘.
```

**제공 코드로 진행하기** — 같은 일을 명령으로 합니다.

```bash
cp -r ~/team-ai-agent-code/ch02/wiki-starter ~/studio-merry-wiki
cd ~/studio-merry-wiki
git init -b main
git add -A
git commit -m "[PM] 팀 위키 시작"
gh repo create studio-merry-wiki --private --source . --push
```

GitHub 웹에서 저장소가 **Private**으로 보이면 완료입니다. 이어서 저장소의 Settings → Collaborators에서 팀원을 초대합니다(도서 부록 B).

### 4-4. 팀 위키 받기 (다른 팀원)

초대 메일이나 https://github.com/notifications 에서 초대를 수락한 뒤 받습니다.

**만들어 보기**

```text
<팀 계정>/studio-merry-wiki 저장소를 ~/studio-merry-wiki 로 받아 줘.
GitHub 로그인 상태부터 확인하고, 실행할 명령을 먼저 보여 줘.
받은 뒤에는 raw 폴더의 파일 목록과 마지막 변경 기록을 보여 줘.
Git 작성자 이름과 메일, 올리기 인증 설정도 확인해 줘.
```

**제공 코드로 진행하기**

```bash
cd ~
gh repo clone <팀 계정>/studio-merry-wiki
```

### 4단계 확인

```bash
ls ~/studio-merry-wiki
cat ~/studio-merry-wiki/.gitignore
git -C ~/studio-merry-wiki log -1 --format="%h %an %s"
```

- [ ] `AGENTS.md README.md guides raw skills wiki`가 보임
- [ ] `.gitignore`에 `.env`와 `*.mp3` 등이 있음
- [ ] 마지막 기록이 팀원끼리 같음
- [ ] GitHub 웹에서 저장소가 Private

**되돌아갈 자리**: 저장소를 잘못 만들었으면 GitHub에서 지우고 4-3을 다시 합니다. 받은 폴더가 꼬였으면 `mv ~/studio-merry-wiki ~/studio-merry-wiki-old`로 보관하고 다시 받습니다. 저장소에 올린 내용은 받은 폴더를 지워도 사라지지 않습니다.

## 5단계. 첫 파일 작업

위키의 원본 폴더에 있는 봉봉소프트 메모를 읽고, 확인된 내용과 빠진 조건을 나눠 저장합니다.

먼저 예제 저장소에서 작업 폴더를 준비합니다.

```bash
cd ~/team-ai-agent-code
python3 run.py prepare --workspace work
```

`work/input`(읽을 자료), `work/output`(결과), `work/prompts`(경로가 채워진 지시문)가 생깁니다. 이미 내용이 있는 폴더는 덮어쓰지 않으므로, 다시 할 때는 `--workspace work-retry`처럼 새 이름을 씁니다.

입력 메모(`~/studio-merry-wiki/raw/20261005_BB_brief.md`)의 내용입니다.

```text
고객사: 봉봉소프트
요청: 제품 소개용 콘텐츠 초안 준비
확인된 내용: 기업 고객 대상, 제공된 제품 소개 사용
미정: 채널·분량·검수 담당자·발행일
```

### 만들어 보기

`hermes chat`을 열고 붙여 넣습니다. 경로는 홈 폴더 기준 그대로 써도 됩니다.

```text
스튜디오 메리의 첫 파일 작업을 진행해 줘.

입력 파일은 ~/studio-merry-wiki/raw/20261005_BB_brief.md 야.
그 파일만 읽고, 고객사·요청 요약·확인된 조건·추가 질문을 정리해 줘.
파일에 없는 날짜, 금액, 담당자는 추측하지 말고 '확인 필요'로 표시해 줘.

먼저 읽은 파일과 결과를 저장할 위치를 알려 줘.
정리한 내용은 ~/team-ai-agent-code/work/output/first-file.md 에 새 마크다운 파일로 저장해 줘.
입력 파일은 수정하지 마.
결과 파일이 이미 있으면 덮어쓰기 전에 물어봐.
저장한 뒤 파일을 다시 읽고 실제 저장 내용과 경로를 알려 줘.
```

### 제공 코드로 진행하기

실행기가 저장된 지시문(`work/prompts/ch02-first-file.txt`)을 헤르메스에 넘기고 결과를 검사합니다. 위 '만들어 보기'를 했다면 이 단계는 건너뛰고 아래 검사만 합니다.

```bash
python3 run.py run ch02-first-file --workspace work
```

모델을 연결하기 전에 결과 형식만 보려면 `--reference`를 붙입니다. 저자가 만든 비교용 결과를 복사할 뿐이므로 모델 실행 결과로 보지 않습니다.

### 결과 확인

```bash
python3 run.py check ch02-first-file --workspace work
cat work/output/first-file.md
git -C ~/studio-merry-wiki status --short
```

- [ ] 고객사가 봉봉소프트이고 다른 고객이 섞이지 않음
- [ ] 추가 질문에 채널·분량·검수 담당자·발행일 네 가지가 모두 있음
- [ ] 미정인 발행일이나 담당자를 지어내지 않음
- [ ] `git status`에 아무것도 나오지 않음(위키 원본을 고치지 않음)

비교용 결과: [completed/first-file.md](completed/first-file.md). 문장이 달라도 네 항목이 맞으면 통과입니다.

**개선 한 번**: `추가 질문을 고객에게 확인할 순서로 다시 정리해 줘`라고 요청하고, 입력에 없던 조건이 끼어들지 않는지 봅니다.

**되돌아갈 자리**: `python3 run.py prepare --workspace work-retry`로 새 작업 폴더를 만들어 다시 합니다.

---

## 확장 노트

파이썬으로 간단한 프로그램을 작성해 본 독자를 위한 내용입니다. 건너뛰어도 3장을 시작할 수 있습니다.

### 실행기의 구조

[../run.py](../run.py)는 세 명령으로 실습을 다룹니다.

| 명령 | 하는 일 | 볼 함수 |
|---|---|---|
| `prepare` | 장 폴더들의 `start/`를 `work/input`에 모으고, 연습 위키 `work/wiki`를 만들고, 지시문의 `{{INPUT}}`·`{{WIKI}}`·`{{OUTPUT}}`을 실제 경로로 채우고, 입력 해시를 저장 | `prepare()` |
| `run` | 모델 실습이면 `hermes chat --oneshot --query-file`로 지시문을 넘기고(헤르메스가 없으면 `--engine api`로 상용 API에 직접), 모델이 필요 없는 실습은 코드로 처리 | `run_task()` |
| `check` | 결과 파일의 존재와 필수 항목, 입력이 바뀌지 않았는지 검사 | `verify()` |

실습 목록은 장 폴더마다 있는 `tasks.json`(이 장은 [tasks.json](tasks.json))에 있습니다. 자기 팀 메모로 실습 하나를 더하려면 이 장의 `start/`에 메모를 넣고, `prompts/`에 지시문을 만들고, `tasks.json`에 항목을 추가한 뒤 새 작업 폴더로 `prepare → run → check`를 실행합니다.

### 위키 동기화 실행 파일 시험

3장에서 쓸 [wiki-starter/skills/wiki-sync/scripts/wiki_sync.py](wiki-starter/skills/wiki-sync/scripts/wiki_sync.py)는 두 팀원이 같은 저장소를 쓰는 상황을 로컬에서 만들어 시험할 수 있습니다. GitHub 계정 없이 동작합니다.

```bash
cd ~/team-ai-agent-code
python3 -m unittest discover -s ch02/tests -v
```

고른 파일만 기록하는지, `.env`를 거부하는지, 충돌이나 올리기 거부에서 멈추는지, 되돌려도 이력이 남는지를 확인합니다.

다음 장: [../ch03/README.md](../ch03/README.md)
