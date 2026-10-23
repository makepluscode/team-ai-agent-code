# 팀 AI 에이전트 실전 — 예제 코드

『팀 AI 에이전트 실전』의 실습 예제입니다. 장과 예제 순서대로 폴더를 나눴고, 예제 폴더 하나에 그 실습에 필요한 지시문·입력 자료·비교용 결과·확인 스크립트가 모두 들어 있습니다.

## 예제 구성

| 디렉터리 | 주제 | 책 |
|---|---|---|
| [ch01/01-hello-jarvis](ch01/01-hello-jarvis/) | 연결 확인, SOUL.md로 이름 붙이기, 메모리 저장·확인·삭제 | 1.2.4항·1.2.5항·1.4절 |
| [ch01/02-notice-check](ch01/02-notice-check/) | 온보딩 안내문의 자료 경로를 자료함에서 확인해 점검표 저장 | 1.3절 |
| [ch02/01-answer-rules](ch02/01-answer-rules/) | 에이전트 답변 규칙 적용과 전후 비교 | 2.1절 |
| [ch02/02-organize-notes](ch02/02-organize-notes/) | 회의 노트·업무 노트·메신저 자료 12개 정리 | 2.2절 |
| [ch02/03-compare-meetings](ch02/03-compare-meetings/) | 지난주·이번 주 주간회의 비교표 | 2.3절 |
| [ch03/01-onboarding-guide](ch03/01-onboarding-guide/) | 온보딩 가이드 잠정안 | 3.1절 |
| [ch03/02-weekly-report](ch03/02-weekly-report/) | 노트 8개로 주간 보고 | 3.2절 |
| [ch03/03-weekly-skill](ch03/03-weekly-skill/) | 주간 보고 스킬 등록과 짧은 요청 재실행 | 3.3절 |
| [ch03/04-weekly-schedule](ch03/04-weekly-schedule/) | 금요일 개인 예약 등록·즉시 실행·중지 | 3.4절 |
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

받은 저장소의 예제 폴더에 들어가 바로 실행합니다. 실습 결과는 예제 폴더의 output/·state/에 생기며 Git이 추적하지 않습니다. 처음부터 다시 할 때는 예제 폴더에서 `uv run reset.py`를 실행합니다. 지울 결과와 되돌릴 제공 파일(4장부터 wiki/·raw/)을 보여 주고 y/N을 물은 뒤 받은 처음 상태로 되돌리며, 헤르메스 설정(~/.hermes)은 바꾸지 않습니다. 예제를 갱신하려면 reset.py로 되돌린 뒤 `git -C ~/team-ai-agent/code pull`을 실행합니다.

```bash
git clone https://github.com/makepluscode/team-ai-agent-code.git ~/team-ai-agent/code
cd ~/team-ai-agent/code/ch01/02-notice-check
hermes chat --query-file prompt.md
uv run check.py
```

- `hermes chat --query-file prompt.md`: prompt.md를 첫 요청으로 보내고 대화를 이어 갑니다. 끝나면 `/exit`.
- `uv run check.py`: 표준 라이브러리만 쓰는 확인 스크립트입니다. 원본 보존·결과 저장처럼 기계로 판정할 수 있는 것만 판정하고, 내용이 맞는지는 '사람이 확인할 항목'으로 보여 줍니다.
- `uv run reset.py`: 예제 폴더를 받은 처음 상태로 되돌립니다(다시 할 때).
- expected/는 저자가 편집한 비교용 결과이며 실제 모델 응답이 아닙니다.

## 예제 폴더의 파일

| 파일 | 역할 |
|---|---|
| README.md | 예제가 하는 일·실행 명령·폴더 구성 |
| prompt.md | 헤르메스에 보내는 지시문 |
| SOUL.md | 이름·역할·말투를 정하는 기본 규칙(~/.hermes/SOUL.md로 복사해 적용) |
| input/ | 지시문이 읽는 원본(합성 자료). 실습 중에 고치지 않습니다 |
| expected/ | 비교용 편집 결과 |
| skills/ | 헤르메스 스킬(~/.hermes/skills/로 복사해 등록) |
| check.py, pyproject.toml | 결과 확인 스크립트와 uv 실행 설정 |

코드 주석은 한국어로 씁니다. 파일 머리 설명에 무엇·입력·출력·실행을 적고, 실제 처리 단계에만 `# 1. …` 번호 주석을 붙입니다.

## 검사

```sh
uv run --extra dev python -m pytest tests legacy/ch02/tests -q
```

---

## 제공 코드(src/team_work/)

예제 폴더의 main.py가 부르는 제공 코드입니다. 이전 실습 경로 `src/team_work/`와 `examples/`를 사용합니다. `book-exercises.yaml`은 장→시작 자료·지시문·편집 비교 결과·명령·확인 기준 연결표입니다. 파일 내용은 JSON 호환 YAML입니다. 구판 legacy/chNN/·run.py·part3.py·wiki.py는 재현용으로 보존합니다. examples/documents/ch01~ch03은 1~3장 예제 폴더로 옮기기 전 구성이며 prepare 호환을 위해 남겨 둡니다.

```sh
uv sync --extra dev
uv run team-work --help
uv run team-work prepare --chapter 1 --workspace work/ch01
uv run team-work verify --workspace work/ch01
uv run team-work bundle --chapter 1 --destination dist/ch01.zip
uv run team-work reference --chapter 1
uv run python -m pytest tests legacy/ch02/tests -q
```

독자 배포의 기본 경로는 이 저장소를 `git clone https://github.com/makepluscode/team-ai-agent-code.git code`로 받는 것입니다(출간 이후 공개로 전환하면 계정 불필요. 집필 중에는 비공개). 보조 배포 자료는 세 종류입니다. `uv build --sdist`의 소스 압축은 pyproject.toml·src/·examples/·공통 호출과 연결표를 포함하므로 Git 계정 없이 내려받아 풀고 그 폴더에서 uv 명령을 실행합니다. `team-work bundle`은 한 장의 일반 폴더·지시문·편집 비교 자료만 묶으며 파이썬 코드 전체 배포를 대신하지 않습니다. `uv build --wheel` 결과는 설치용 패키지이며 예제 자료와 기존 공통 모듈·위키 동기화 실행 파일도 포함합니다. 로컬 생성·분리 설치는 검사했고 외부 발행·업로드는 하지 않았습니다.

1~3장 준비는 Git/위키 없이 일반 input/·prompts/·output/ 폴더를 만듭니다. bundle 압축도 Git 계정 없이 풀어 같은 일반 폴더 자료로 사용합니다. 4장부터 raw/·wiki/·규칙 파일을 명시 준비합니다. prepare는 비어 있는 폴더만 사용하며 reference를 실제 output/에 복사하지 않습니다. 각 예제 README와 RECOVERY를 따릅니다. 코드 실행은 이 code/ 소스 배포 폴더에서 합니다.

문서 생성은 기존 llm.py 공통 상용 호출을 재사용합니다. Claude 기준 `ANTHROPIC_API_KEY`와 공식 문서에서 확인한 `TEAM_AGENT_MODEL` 환경 변수가 필요합니다. 레거시 기본 모델명을 새 경로가 자동 사용하지 않습니다. 키를 Git·결과·로그에 쓰지 않습니다. 생성 성공은 업무 승인과 구별하며 실패 기록도 남깁니다. OpenAI/Gemini 전환·Hermes 설치/등록·실제 API·Windows WSL2/Mac 장비는 TODO(검증)입니다.

`input/my-instructions.md`는 독자가 말투·불확실성 기준을 바꾸는 설정입니다. 업무 원본의 불변 해시와 구별하며 생성 기록에는 실제 사용한 파일 경로를 남깁니다.

백업은 실행 중인 개인 예약·팀 작업의 잠금이 있으면 멈춥니다. SQLite는 backup API로 일관된 사본을 만들고 무결성을 확인하며, 복구는 새 폴더에 해시와 DB 무결성을 확인한 뒤 수행합니다. 공동 운영 전체의 장비·권한 검증은 남아 있습니다.

6장 음원은 제작 전이며 합성 대본 대안으로 이어 갑니다. 실제 음원 전사·원음 구간 대조는 미완료입니다. 선택 전사 환경은 `uv sync --extra transcription`으로 분리했습니다. 5장 두 폴더는 로컬 인계이며 실제 계정 초대 검증이 아닙니다.

---

## 구판 자료

아래는 기존 패키지의 재현 안내입니다. v1.7 장 번호·데이터·완료 기준과 구별합니다.

# 팀 AI 에이전트 실전 — 예제 코드 및 대시보드 저장소

이 저장소는 『팀 AI 에이전트 실전』 도서의 장별 실습 코드와 통합 팀 대시보드 구현체를 담고 있습니다.

## 장별 실습

장마다 폴더가 있고, 각 폴더의 README.md만 보고 실습을 처음부터 끝까지 따라 할 수 있습니다. 본문은 윈도우(WSL2) 기준입니다.

| 장 | 실습 안내 | 이 장에서 손에 쥐는 것 |
|---|---|---|
| 1장 완성 화면과 전체 구조 | [legacy/ch01/README.md](legacy/ch01/README.md) | 완성 화면 읽기, 팀 위키 구조, 위키에 넣을 첫 자료 작업지 |
| 2장 설치와 팀 위키 받기 | [legacy/ch02/README.md](legacy/ch02/README.md) | 헤르메스·AI 챗봇 연결, 팀 위키 저장소, 첫 파일 작업 |
| 3장 팀 위키에 기준 쌓기 | [legacy/ch03/README.md](legacy/ch03/README.md) | 레시피 열두 개, 위키 정리와 동기화, 스킬 배포, 예약 |
| 4장 콘텐츠 업무 자동화 | [legacy/ch04/README.md](legacy/ch04/README.md) | 조사·SNS·뉴스레터·주간 보고와 캠페인 페이지 |
| 5장 외부 서비스 연결과 위키 쌓기 | [legacy/ch05/README.md](legacy/ch05/README.md) | 메일·캘린더·알림 연결, 변경 규칙, 드라이브 사본 |
| 6장 예약 실행과 비용 | [legacy/ch06/README.md](legacy/ch06/README.md) | 업무시간 예약, 아침 브리핑, 사용량 기록, 운영 기준 페이지 |
| 7장 문의 분류와 담당 지정 | [legacy/ch07/README.md](legacy/ch07/README.md) | 조회 전용 MCP, 상용·로컬 판정, 판정 경로 결정 페이지 |
| 8장 견적 초안과 사람의 확인 | [legacy/ch08/README.md](legacy/ch08/README.md) | 견적 계산, 사람 확인 이력, 판단 기준 페이지와 반영 전후 비교 |
| 9장 회의 자동화 | [legacy/ch09/README.md](legacy/ch09/README.md) | 로컬 전사, 회의록 추출, 결정 페이지 |

### 폴더 구성

```text
team-ai-agent-code/
├── run.py        # 2~6장 실습 실행기(prepare·list·prompt·run·check·mcp-config)
├── part3.py      # 7~9장 실습 실행기(판정·라우팅·견적·상태·확인·전사 후처리·위키)
├── wiki.py       # 연습 팀 위키: 만들기·원본 넣기·정리·검사·드라이브 내보내기
├── llm.py        # 헤르메스 없이 상용 API(클로드·OpenAI·제미나이)를 직접 부르는 경로
├── legacy/ch01/ … legacy/ch09/ # 장 폴더
│   ├── README.md      # 그 장의 실습 안내
│   ├── tasks.json     # 실습 정의(입력·결과·확인 기준, 위키 정리 실습)
│   ├── start/         # 시작 자료(합성)
│   ├── prompts/       # 지시문 파일
│   ├── completed/     # 비교용 결과, 그 장 끝 상태의 비교용 위키(studio-merry-wiki/)
│   └── wiki-raw/      # 위키에 넣을 원본의 패키지 판
└── tests/test_practice_*.py   # 실행기 시험
```

장 폴더에는 그 장의 자료만 둡니다. `run.py prepare`는 2~6장의 `start/`를 작업 폴더 `work/input`에 모으고 연습 위키 `work/wiki`를 만듭니다. `part3.py prepare`는 7~9장 자료를 모읍니다. 앞 장을 건너뛰려면 `--wiki-from chNN`으로 그 장 끝 상태의 위키에서 시작합니다.

```bash
python3 run.py prepare --workspace work
python3 run.py list
python3 run.py run ch04-sns --workspace work                  # 헤르메스
python3 run.py run ch04-sns --workspace work --engine api     # 상용 API 직접(키는 환경 변수)
python3 part3.py prepare --workspace work-part03
python3 -m unittest tests/test_practice_run.py tests/test_practice_part3.py
python3 -m unittest discover -s legacy/ch02/tests                     # 위키 동기화 실행 파일 시험
```

### 확인 범위

2026-10-15 저자 Linux 장비에서 제공 코드 전체와 상용 API 직접 호출 경로(제미나이 2.5 Flash)를 실행했습니다. 헤르메스 경로, Laya, 실서비스 계정, 두 기준 장비(Windows+WSL2, Mac mini M4 16GB)는 확인 전입니다. 비교용 결과는 저자가 작성한 예시이며 모델 응답이 아닙니다. 도서 저장소의 `run-all-examples` 스킬이 전체 실습을 한 번에 돌리고 리포트를 남깁니다.

## 이전 구성의 대시보드 시제품

이하 src와 docs/prd는 이전 9장 구성의 시제품입니다. 장 번호·생성용 로컬 모델·GPU 요건을 현재 책의 실습 요건으로 사용하지 않습니다. 최신 구성으로의 재매핑은 후속 작업입니다.

## 기술 스택 및 환경 기준

- **운영체제 및 하드웨어**: Windows 11 + WSL2 (Ubuntu 22.04 LTS), NVIDIA GPU (VRAM 12GB+, RTX 3060 기준)
- **로컬 LLM 런타임**: Ollama (`qwen3.5:9b`), 로컬 Whisper
- **웹 대시보드**: FastAPI + HTMX + Jinja2 (반응형 단일 페이지 대시보드)
- **에이전트 및 연동**: Hermes Agent, MCP(Model Context Protocol) Python SDK, SQLite
- **패키지 관리**: uv (`uv sync`, `uv run`)

## 디렉터리 구성

```text
team-ai-agent-code/
├── docs/prd/             # 각 장별 코드 기획 및 PRD (Codex & Claude 협업 기획안)
│   ├── ch01_overview.md
│   ├── ch02_hello_dashboard.md
│   ├── ch03_wiki_agent.md
│   ├── ch04_secure_db_mcp.md
│   ├── ch05_meeting_minutes.md
│   ├── ch06_work_recipes.md
│   ├── ch07_team_dashboard.md
│   ├── ch08_leak_inspection.md
│   └── ch09_ops_deploy.md
├── src/
│   ├── app/              # FastAPI + HTMX 팀 대시보드 (2장 뼈대 및 7장 완성본)
│   ├── mcp/              # 4장 사내 DB(SQLite) 조회 전용 MCP 서버 및 가명화 모듈
│   ├── wiki/             # 3장 사내 LLM 위키 검색 및 수집 도구
│   ├── whisper/          # 5장 로컬 음성 전사 및 구조화 회의록 추출
│   ├── recipes/          # 6장 업무 레시피 (문의 분류, 견적서, 브리핑)
│   └── audit/            # 8장 카나리아 토큰 및 감사 로그 누출 점검기
├── tests/                # 기능별 단위/통합 테스트
├── captures/             # 실제 실행 캡처 이미지
├── PRD.md                # 전체 통합 아키텍처 및 요구사항 정의서
└── pyproject.toml
```

## 빠른 시작

```bash
# 의존성 설치
uv sync

# 대시보드 실행
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```
