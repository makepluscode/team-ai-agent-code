# 7장 문의 분류와 담당 지정

『팀 AI 에이전트 실전』 7장의 실습 안내입니다. 대표 문의 메일함에 들어온 문의를 유형·긴급도·담당 직군으로 판정하고, 판정 경로(상용·Laya·Decision API)를 비교해 고른 경로를 위키 결정 페이지로 남깁니다.

- 원고: `content/ch07_inquiry-routing_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/)(문의 30건·질문·규칙·고객), 지시문 [prompts/](prompts/), 실습 정의 [tasks.json](tasks.json), 위키 원본 [wiki-raw/](wiki-raw/)
- 조회 전용 MCP 서버: [mcp_server.py](mcp_server.py), 연결 시험: [check_mcp.py](check_mcp.py)
- 의존성: [requirements-mcp.txt](requirements-mcp.txt), Laya 파이썬 대안 [requirements-laya.txt](requirements-laya.txt)
- 실행기: 저장소 맨 위의 [../part3.py](../part3.py)(7~9장 공통)
- 7장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)

> 확인 범위: 조회 MCP의 stdio 연결과 상용 판정 경로(`--transport api`, 제미나이 2.5 Flash로 30건)를 2026-10-15에 실행했습니다. Laya(올라마 MLX 태그·파이썬 경로)와 Decision API, 두 기준 장비는 확인 전입니다. 문의 30건은 개발용 미리보기이고 정답은 저자 검수 전 초안입니다. 평가 90건은 아직 없습니다.

## 준비

```bash
cd ~/team-ai-agent-code
python3 part3.py prepare --workspace work-part03     # input(정답 포함)·model-input(정답 제외)·연습 위키(6장 끝 상태)
```

`--wiki-from ch05`처럼 위키 시작 상태를 바꾸거나 `--no-wiki`로 위키 없이 준비합니다.

## 7.1 조회 전용 MCP 서버

```bash
python3 part3.py database --workspace work-part03     # output/team.db (정답 라벨 없음)
python3 part3.py mcp-config --workspace work-part03   # 헤르메스 설정에 합칠 항목
uv run --no-project --python 3.11 --with-requirements ch07/requirements-mcp.txt python ch07/check_mcp.py
```

도구는 `get_inquiry`·`get_customer`·`get_price` 세 개뿐이고 DB는 `mode=ro`로 엽니다. 판정·담당·견적·상태는 애플리케이션이 `output/`에 씁니다.

## 7.2~7.3 상용 판정과 담당 제안

| 명령 | 하는 일 |
|---|---|
| `decide --inquiry <ID> --transport api` | [prompts/ch07-classify.txt](prompts/ch07-classify.txt)와 질문 파일을 상용 API에 보내고, Laya와 같은 형식(answers·_meta)으로 `output/decisions/<ID>.json` 저장. processing_location cloud, 토큰 기록 |
| `decide-all --transport api` | 30건을 차례로 판정·라우팅(이미 있는 결과는 건너뜀) |
| `route --inquiry <ID>` | 임계값(0.85, 설명용)·계약 중단(0.5)·클레임·일정/견적 규칙으로 확인 이유를 붙이고 `output/routing/`에 저장. 사람 배정은 하지 않음 |

```bash
python3 part3.py decide --workspace work-part03 --inquiry INQ-BB-D01-A --transport api
python3 part3.py route --workspace work-part03 --inquiry INQ-BB-D01-A
python3 part3.py decide-all --workspace work-part03 --transport api
```

공급자는 환경 변수의 키로 고릅니다(`ANTHROPIC_API_KEY` → 클로드, `OPENAI_API_KEY`, `GEMINI_API_KEY`). `TEAM_AGENT_PROVIDER`·`TEAM_AGENT_MODEL`로 바꿉니다. 제공 규칙에서는 견적 문의 D01도 '일정·견적 조건 확인'으로 review_required가 됩니다(원고 7.3).

판정 서버 없이 흐름만 보려면 `decide --reference`(저자 작성 판정, simulation 표시)를 씁니다.

## 7.4 판정 경로 고르기

```bash
python3 part3.py request --workspace work-part03                       # Laya 요청 본문
ollama pull laya:322m-multilingual-mlx-fp16                            # 맥: 올라마. WSL2는 확인 전
python3 part3.py decide --workspace work-laya --inquiry INQ-BB-D02-A   # --transport ollama(기본)
python3 part3.py compare --workspace work-part03 --dev                 # 내 판정 결과를 개발 묶음 정답 초안과 대조
```

`compare --dev`는 `development_accuracy`를 내지만 `accuracy`는 null입니다. 개발 묶음(정답 초안 30건)으로 임계값을 고르는 용도이고 평가 결과로 쓰지 않습니다. 평가 묶음은 `compare --predictions <측정 기록>`(split evaluation, data_origin measured만 받음)으로 잽니다.

## 위키에 넣기 — `ch07-route-record`

비교 결과와 고른 경로를 원본 [wiki-raw/20261013_TEAM_judgment-route.md](wiki-raw/20261013_TEAM_judgment-route.md)로 넣고 결정 페이지 `wiki/decisions/20261013_judgment-route.md`로 정리합니다. 자기 원본이 있으면 `work-part03/output/judgment-route.md`에 두면 그 파일을 씁니다.

```bash
python3 part3.py wiki ch07-route-record --workspace work-part03 --engine api
```

자동 검사: 결정 페이지에 0.85·'확인 필요'(측정 전 값)·운영 기준 페이지(operating-rules) 연결.

## 되돌아갈 자리

- 문의·질문·규칙: [start/](start/), 비교 구조: [start/comparison-structure.json](start/comparison-structure.json)
- 코드: [../part3.py](../part3.py)의 `request_body`(정답 제외), `commercial_decide`, `decide`, `routing`
