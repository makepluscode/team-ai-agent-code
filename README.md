# 팀 AI 에이전트 실전 — 예제 코드 및 대시보드 저장소

이 저장소는 『팀 AI 에이전트 실전』 도서의 장별 실습 코드와 통합 팀 대시보드 구현체를 담고 있습니다.

## 장별 실습

장마다 폴더가 있고, 각 폴더의 README.md만 보고 실습을 처음부터 끝까지 따라 할 수 있습니다. 본문은 윈도우(WSL2) 기준입니다.

| 장 | 실습 안내 | 이 장에서 손에 쥐는 것 |
|---|---|---|
| 1장 완성 화면과 전체 구조 | [ch01/README.md](ch01/README.md) | 완성 화면 읽기, 팀 위키 구조, 위키에 넣을 첫 자료 작업지 |
| 2장 설치와 팀 위키 받기 | [ch02/README.md](ch02/README.md) | 헤르메스·상용 AI 연결, 팀 위키 저장소, 첫 파일 작업 |
| 3장 팀 위키에 기준 쌓기 | [ch03/README.md](ch03/README.md) | 레시피 열두 개, 위키 정리와 동기화, 스킬 배포, 예약 |
| 4장 콘텐츠 업무 자동화 | [ch04/README.md](ch04/README.md) | 조사·SNS·뉴스레터·주간 보고와 캠페인 페이지 |
| 5장 외부 서비스 연결과 위키 쌓기 | [ch05/README.md](ch05/README.md) | 메일·캘린더·알림 연결, 변경 규칙, 드라이브 사본 |
| 6장 예약 실행과 비용 | [ch06/README.md](ch06/README.md) | 업무시간 예약, 아침 브리핑, 사용량 기록, 운영 기준 페이지 |
| 7장 문의 분류와 담당 지정 | [ch07/README.md](ch07/README.md) | 조회 전용 MCP, 상용·로컬 판정, 판정 경로 결정 페이지 |
| 8장 견적 초안과 사람의 확인 | [ch08/README.md](ch08/README.md) | 견적 계산, 사람 확인 이력, 판단 기준 페이지와 반영 전후 비교 |
| 9장 회의 자동화 | [ch09/README.md](ch09/README.md) | 로컬 전사, 회의록 추출, 결정 페이지 |

### 폴더 구성

```text
team-ai-agent-code/
├── run.py        # 2~6장 실습 실행기(prepare·list·prompt·run·check·mcp-config)
├── part3.py      # 7~9장 실습 실행기(판정·라우팅·견적·상태·확인·전사 후처리·위키)
├── wiki.py       # 연습 팀 위키: 만들기·원본 넣기·정리·검사·드라이브 내보내기
├── llm.py        # 헤르메스 없이 상용 API(클로드·OpenAI·제미나이)를 직접 부르는 경로
├── ch01/ … ch09/ # 장 폴더
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
python3 -m unittest discover -s ch02/tests                     # 위키 동기화 실행 파일 시험
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
