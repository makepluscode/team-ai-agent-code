# 팀 AI 에이전트 실전 — 예제 코드 및 대시보드 저장소

이 저장소는 『팀 AI 에이전트 실전』 도서의 장별 실습 코드와 통합 팀 대시보드 구현체를 담고 있습니다.

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
