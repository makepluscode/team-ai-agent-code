# 팀 AI 에이전트 실전 — 예제 코드

『팀 AI 에이전트 실전』의 실습 예제입니다. 장과 예제 순서대로 폴더를 나눴고, 예제 폴더 하나에 그 실습에 필요한 지시문·입력 자료·비교용 결과·확인 스크립트가 모두 들어 있습니다.

책에 나오는 설치 명령·실습 명령·대화창 지시문은 [COMMANDS.md](COMMANDS.md)에 순서대로 모여 있습니다. 책을 보고 직접 치지 말고 이 파일에서 복사해 붙여 넣으세요.

## 예제 구성

| 디렉터리 | 주제 | 책 |
|---|---|---|
| [ch01/01-hello-jarvis](ch01/01-hello-jarvis/) | 연결 확인, SOUL.md로 이름 붙이기, 메모리 저장·확인·삭제 | 사용 설명서·1.2.2절·1.4절 |
| [ch01/02-notice-check](ch01/02-notice-check/) | 안내문의 자료 경로 세 개를 자료함에서 확인해 표로 저장 | 1.3절 |
| [ch02/01-answer-rules](ch02/01-answer-rules/) | 에이전트 답변 규칙 적용과 전후 비교 | 2.1절 |
| [ch02/02-organize-notes](ch02/02-organize-notes/) | 회의 노트·업무 노트·메신저 자료 12개 정리 | 2.2절 |
| [ch02/03-compare-meetings](ch02/03-compare-meetings/) | 지난주·이번 주 주간회의 비교표 | 2.3절 |
| [ch03/01-weekly-report](ch03/01-weekly-report/) | 노트 8개로 주간 보고 | 3.1절 |
| [ch03/02-weekly-skill](ch03/02-weekly-skill/) | 주간 보고 스킬 등록과 짧은 요청 재실행 | 3.2절 |
| [ch03/03-weekly-schedule](ch03/03-weekly-schedule/) | 금요일 개인 예약 등록·즉시 실행·중지 | 3.3절 |
| [ch04/01-wiki-folder](ch04/01-wiki-folder/) | 로컬 위키 폴더와 정리 규칙 확인 | 4.1~4.2절 |
| [ch04/02-first-page](ch04/02-first-page/) | 첫 위키 페이지 정리 | 4.3절 |
| [ch04/03-source-query](ch04/03-source-query/) | 위키 출처 조회 | 4.4절 |
| [ch05/01-share-repo](ch05/01-share-repo/) | 팀 위키 저장소 준비 | 5.1절 |
| [ch05/02-wiki-sync](ch05/02-wiki-sync/) | 위키 동기화 스킬 | 5.2절 |
| [ch05/03-change-memo](ch05/03-change-memo/) | 동료의 변경 메모 반영 | 5.3절 |
| [ch05/04-member-revision](ch05/04-member-revision/) | 위키를 받은 동료의 결과 수정 | 5.4절 |
| [ch05/05-skill-share](ch05/05-skill-share/) | 공유 스킬 배포 | 5.5절 |
| [ch06/01-meeting-input](ch06/01-meeting-input/) | 회의 입력 자료와 로컬 전사 | 6.1~6.2절 |
| [ch06/02-meeting-notes](ch06/02-meeting-notes/) | 회의 결정과 할 일 추출 | 6.3절 |
| [ch06/03-decision-wiki](ch06/03-decision-wiki/) | 회의 결정의 위키 반영 | 6.4절 |
| [ch07/01-request-intake](ch07/01-request-intake/) | 내부 요청 접수와 처리 기록 | 7.1~7.2절 |
| [ch07/02-mcp-lookup](ch07/02-mcp-lookup/) | 조회 전용 MCP 연결 | 7.3절 |
| [ch07/03-mail-input](ch07/03-mail-input/) | 추가 입력 경로인 메일 | 7.4절 |
| [ch08/01-classify-requests](ch08/01-classify-requests/) | 요청 분류와 담당 제안 | 8.1~8.3절 |
| [ch08/02-compare-paths](ch08/02-compare-paths/) | 판정 경로 비교 | 8.4절 |
| [ch09/01-review-inputs](ch09/01-review-inputs/) | 검토 대상 점검과 확인 기준 | 9.1~9.2절 |
| [ch09/02-review-and-fix](ch09/02-review-and-fix/) | 수정 요청과 다시 확인 | 9.3절 |
| [ch09/03-criteria-wiki](ch09/03-criteria-wiki/) | 판단 기준의 위키 반영 | 9.4절 |
| [ch10/01-revision-search](ch10/01-revision-search/) | 문서 버전 관리와 위키 검색 | 10.1~10.2절 |
| [ch10/02-source-answers](ch10/02-source-answers/) | 출처가 있는 답변 | 10.3절 |
| [ch10/03-wiki-audit](ch10/03-wiki-audit/) | 모순과 오래된 기록 점검 | 10.4절 |
| [ch11/01-team-hermes](ch11/01-team-hermes/) | 헤르메스 한 대로 모으기 | 11.1절 |
| [ch11/02-team-dashboard](ch11/02-team-dashboard/) | 팀 대시보드 조회와 동료 접속 | 11.2~11.4절 |
| [ch12/01-dashboard-work](ch12/01-dashboard-work/) | 대시보드에서 지시와 상태 변경 | 12.1~12.2절 |
| [ch12/02-morning-briefing](ch12/02-morning-briefing/) | 회의록과 아침 브리핑 통합 | 12.3절 |
| [ch12/03-hours-backup](ch12/03-hours-backup/) | 업무시간 운영과 백업·복구 | 12.4절 |

4~12장 예제 폴더는 `tools/make_chapter_examples.py`가 `tools/chapter_example_specs.py`의 명세로 만듭니다. 예제를 고칠 때는 명세를 고친 뒤 `python3 tools/make_chapter_examples.py`로 다시 만듭니다. 4장부터는 확정적인 처리를 예제 폴더의 main.py가 맡습니다(`uv run main.py <단계>`, 단계 목록은 main.py 머리 설명).

## 실행 방법

받은 저장소의 예제 폴더에 들어가 바로 실행합니다. 실습 결과는 예제 폴더의 output/·state/에 생기며 Git이 추적하지 않습니다. 처음부터 다시 할 때는 예제 폴더에서 `uv run reset.py`를 실행합니다. 지울 결과(1~3장은 output/, 4장부터는 output/·state/와 되돌릴 wiki/·raw/)를 보여 주고 y/N을 물은 뒤 받은 처음 상태로 되돌리며, 헤르메스 설정(~/.hermes)은 바꾸지 않습니다. 예제를 갱신하려면 reset.py로 되돌린 뒤 `git -C ~/team-ai-agent/code pull`을 실행합니다.

```bash
git clone https://github.com/makepluscode/team-ai-agent-code.git ~/team-ai-agent/code
cd ~/team-ai-agent/code/ch02/02-organize-notes
hermes chat --query-file prompt.md
uv run check.py
```

- `hermes chat --query-file prompt.md`: prompt.md를 첫 요청으로 보내고 대화를 이어 갑니다. 끝나면 `/exit`.
- `uv run check.py`: 1~3장에서는 파일 12개를 정리하는 ch02/02-organize-notes에만 있고, 나머지 1~3장 예제는 결과 파일을 직접 열어 README의 '확인할 것'과 대조합니다. 4장부터는 예제마다 있습니다. 표준 라이브러리만 씁니다. 원본 보존·결과 저장처럼 기계로 판정할 수 있는 것만 판정하고, 내용이 맞는지는 '사람이 확인할 항목'으로 보여 줍니다.
- `uv run reset.py`: 예제 폴더를 받은 처음 상태로 되돌립니다(다시 할 때). 1~3장은 output/만 지웁니다.
- expected/는 편집한 비교용 결과이며 실제 모델 응답이 아닙니다.

## 예제 폴더의 파일

| 파일 | 역할 |
|---|---|
| README.md | 예제가 하는 일·실행 명령·폴더 구성 |
| prompt.md | 헤르메스에 보내는 지시문 |
| SOUL.md | 이름·역할·말투를 정하는 기본 규칙(~/.hermes/SOUL.md로 복사해 적용) |
| input/ | 지시문이 읽는 원본(합성 자료). 실습 중에 고치지 않습니다 |
| expected/ | 비교용 편집 결과 |
| skills/ | 헤르메스 스킬(~/.hermes/skills/로 복사해 등록) |
| check.py | 결과 확인 스크립트(1~3장은 ch02/02-organize-notes에만, 4장부터는 예제마다) |
| pyproject.toml, reset.py | uv 실행 설정과 다시 하기 스크립트(모든 예제) |

코드 주석은 한국어로 씁니다. 파일 머리 설명에 무엇·입력·출력·실행을 적고, 실제 처리 단계에만 `# 1. …` 번호 주석을 붙입니다.

## 저장소 구성

```text
team-ai-agent-code/
├── ch01/ … ch12/          # 장별 예제 폴더(chNN/NN-예제이름/). 독자가 실습하는 곳
├── src/team_work/         # 4장부터 예제 폴더의 main.py가 부르는 제공 코드
├── examples/              # 4~12장 예제 폴더를 만드는 시작 자료(생성기 입력)
├── tools/                 # 4~12장 예제 생성기와 명세
├── tests/                 # 예제 폴더와 제공 코드 시험
├── book-exercises.yaml    # 장 → 예제 폴더·지시문·명령·확인 기준 연결표(JSON 호환 YAML)
└── pyproject.toml, uv.lock
```

## 제공 코드(src/team_work/)

4장부터 위키·요청 기록·대시보드처럼 확정적인 처리를 맡습니다. 독자는 예제 폴더에서 `uv run main.py <단계>`로 부르고, 직접 import하지 않습니다. 인자 없이 `uv run main.py`를 실행하면 실행 순서와 단계 목록이 나옵니다.

- 위키 페이지는 헤르메스가 output/wiki-draft/에 변경안만 쓰고, `main.py preview`로 차이를 본 뒤 `main.py apply`가 y/N 확인·충돌 검사·백업과 함께 적용합니다.
- 헤르메스 설정(MCP·스킬·SOUL.md·cron)은 `main.py doctor`로 읽기만 하고 바꾸지 않습니다.
- 상용 API 직접 호출(`llm_api.py`)은 헤르메스 없이 시험할 때만 씁니다. 키는 환경 변수(`ANTHROPIC_API_KEY`, `TEAM_AGENT_MODEL`)에서만 읽고 결과·로그에 쓰지 않습니다.

## 4~12장 예제 다시 만들기

4~12장 예제 폴더는 손으로 고치지 않습니다. `tools/chapter_example_specs.py`의 명세를 고친 뒤 다음 명령으로 다시 만듭니다.

```sh
python3 tools/make_chapter_examples.py
```

## 검사

```sh
uv run --extra dev python -m pytest -q tests
```

## 확인 범위

1~3장 예제는 2026-10-25 Windows 11 + WSL2(Ubuntu)와 Mac mini M4(macOS 15)에서 헤르메스 v0.22.5와 claude-haiku-5-5로 이 저장소를 받아 끝까지 실행했습니다. 4~12장은 Windows + WSL2 기준 장비에서 지시문과 main.py 단계를 실행했고, 5장 GitHub 공유 저장소와 공유 스킬 배포, 6장 실제 음원 전사, 7.4절 Gmail 연결, 8.4절 로컬 판정, 맥 기준 장비 전 과정은 확인 전입니다. expected/는 편집한 비교용 결과이며 실제 모델 응답이 아닙니다.
