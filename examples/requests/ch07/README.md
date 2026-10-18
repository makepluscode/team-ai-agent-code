# 7장 독립 실습

합성 입력과 편집 비교 결과(author-reference)입니다. 저자 전건 검수 전이며 실제 모델 응답·실서비스 연결·두 기준 장비 검증을 뜻하지 않습니다.

코드 경로(code/에서 실행):

```sh
uv run team-work prepare --chapter 7 --workspace /tmp/merry-ch07
uv run team-work requests init --workspace /tmp/merry-ch07
uv run team-work requests list --workspace /tmp/merry-ch07
```

지시문 경로: 준비한 prompts/task.md를 헤르메스에 파일로 입력하거나 복사합니다. input/의 시작 자료와 raw/를 읽고 output/에 새 결과를 저장합니다. 준비 시 reference/는 복사하지 않습니다.

복구: 기존 작업 폴더를 보존하고 다른 빈 폴더에 다시 prepare·init합니다. DB를 수동 수정하지 않습니다. 완료 기준은 아래의 장별 확인을 따릅니다.

```sh
uv run team-work requests intake --workspace /tmp/merry-ch07 --input /tmp/merry-ch07/input/internal-requests.json
uv run team-work requests intake --workspace /tmp/merry-ch07 --input /tmp/merry-ch07/input/optional-mail.json
uv run team-work requests-mcp --workspace /tmp/merry-ch07
```

내부8+제공 메일2=요청10건, 원문 SHA256·참조 확인. 같은 입력 재접수는 업무를 늘리지 않습니다. 내부8건만으로 먼저 접수를 끝낸 뒤 메일2건을 추가합니다. MCP 도구는 get_request/get_roles 두 개이며 분류 정답과 쓰기 도구는 노출하지 않습니다. stdio 서버는 호스트가 연결할 때까지 기다립니다. Gmail 실연결은 TODO(검증), 제공 메일로 계속합니다. 주소는 external-01@example.com·external-02@example.com 합성 표기입니다.
공식 MCP SDK: https://py.sdk.modelcontextprotocol.io/run/ (2026-10-18 확인, 설치된 mcp2 MCPServer 사용).
