# 5장 외부 서비스 연결과 위키 쌓기

『팀 AI 에이전트 실전』 5장의 실습 안내입니다. 메일·캘린더·알림을 합성 서비스로 연결해 보고, 통화로 바뀐 발행일을 위키에 기록한 뒤, 위키를 드라이브용 읽기 전용 사본으로 내보냅니다.

- 원고: `content/ch05_service-connections_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/)(합성 메일 스레드 3통·캘린더·사건표), 지시문 [prompts/](prompts/), 실습 정의 [tasks.json](tasks.json), 비교용 결과 [completed/](completed/), 위키 원본 [wiki-raw/](wiki-raw/)
- 합성 MCP 서버: [mcp_server.py](mcp_server.py), 연결 시험: [check_mcp.py](check_mcp.py), 의존성: [requirements-mcp.txt](requirements-mcp.txt)
- 5장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)

> 확인 범위: 합성 MCP 서버의 stdio 연결, 제공 코드, 상용 API로 한 위키 정리를 확인했습니다. 실제 지메일·캘린더·슬랙·카카오톡·드라이브 계정과 OAuth는 확인 전입니다. 드라이브 업로드는 하지 않습니다.

역할: 메일함·캘린더·알림·드라이브 연결은 **PM 한 명**의 헤르메스에만 둡니다. 다른 팀원은 위키를 받아 읽습니다.

## 5.1 MCP 서버 연결

```bash
python3 run.py mcp-config --workspace work           # 헤르메스 설정에 합칠 mcp_servers 항목 출력
uv run --no-project --python 3.11 --with-requirements ch05/requirements-mcp.txt python ch05/check_mcp.py
```

도구 7개: `read_mail`·`save_mail_draft`·`list_calendar`·`propose_calendar`·`notification_draft`·`read_team_document`·`write_team_document`. 발송 도구는 없습니다. 연결 시험은 실제 계정의 인증을 확인하지 않습니다.

## 5.2~5.5 제공 코드(합성 서비스)

| 절 | 실습 ID | 결과 | 자동 확인 |
|---|---|---|---|
| 5.2 | `ch05-mail` | `mail-workflow.json` | 메시지 3통을 읽고 채널 SNS·발행일 10/12를 확인된 조건으로, 질문은 '최종 분량'·'검수 담당자'만. 초안 status draft, external_writes false |
| 5.3 | `ch05-calendar` | `calendar-workflow.json` | CAL-BB-001을 10/12→10/15로 **고치는**(update) 제안, approval_required. 같은 날짜의 잠정 일정 CAL-BB-002(검수 담당자 확인)는 바꾸지 않음 |
| 5.4 | `ch05-notification` | `notification-workflow.json` | 연습 채널 #studio-merry-ops, not_sent, 본문이 위키 페이지 경로를 가리킴 |
| 5.5 | `ch05-document` | `document-workflow.json` | 연습 문서 1판(EV-BB-1005-PLAN)과 2판(EV-BB-1008-CALL) |

```bash
for id in ch05-mail ch05-calendar ch05-notification ch05-document; do python3 run.py run $id --workspace work; done
```

이 명령들은 MCP를 거치지 않고 합성 자료로 예상 결과를 만듭니다. 도구 호출은 5.1의 서버에 직접 요청해 확인합니다.

## 5.5 위키 쌓기 — `ch05-wiki-record`

위키 담당자(PM)가 하는 일 세 가지를 차례로 합니다.

1. 규칙 파일(AGENTS.md)의 '## 목록과 기록' 앞에 변경 규칙 두 줄을 더합니다(제공 코드가 대신 더함).
2. 메일 기록 원본 `raw/20261005_BB_CAMP-BB-202610_mail.md`(주소·이름·서명 없이 확인한 조건만)를 넣고 정리합니다.
3. 통화 원본 `raw/20261008_BB_CAMP-BB-202610_call.md`를 넣고 정리합니다. 원본은 [wiki-raw/](wiki-raw/)에 있습니다.

```bash
python3 run.py prompt ch05-wiki-record --workspace work            # 규칙 두 줄과 원본별 지시문
python3 run.py run ch05-wiki-record --workspace work --engine api
```

자동 검사: 캠페인 페이지에 현재 발행일 2026-10-15, 변경 이력의 2026-10-12, SNS, '확인 필요', 통화 원본 출처, 규칙 파일의 '변경 이력' 문구. 사람이 볼 것: 발행일이 캠페인 페이지 한 곳에만 있는지, 고객 페이지는 연결만 두었는지.

## 5.5 드라이브 내보내기 — `ch05-drive-export`

위키에서 드라이브로 **한쪽 방향**으로만 내보낼 사본 묶음을 로컬에 만듭니다. 업로드는 하지 않습니다.

```bash
python3 run.py run ch05-drive-export --workspace work
python3 wiki.py export --wiki work/wiki --out work/export-2 --previous work/output/drive-export/export-list.json   # 다음 주 내보내기
```

- 내보내는 것: `wiki/index.md`에 있는 고객·캠페인 페이지. `raw/`·`guides/`·`skills/`·`AGENTS.md`는 내보내지 않습니다.
- 폴더: `팀 공유/`와 `<고객ID> 공유/`(한 폴더에 한 고객만)
- 사본 맨 위 머리말: 원본 위치, 내보낸 시각, 내보낸 판(커밋), 수정 요청은 위키 담당자(PM)
- `export-list.json`: 위키 경로·폴더·drive_file_id(업로드 뒤 채움, 지금은 null)·커밋·시각·상태. `--previous`로 지난 목록을 주면 이름이 바뀌었거나 빠진 페이지를 '삭제'로 표시합니다.

실제 드라이브 업로드는 PM의 헤르메스(드라이브 MCP)에 [prompts/ch05-drive-export.txt](prompts/ch05-drive-export.txt)를 넘겨 합니다. 쓸 MCP 서버와 마크다운→구글 문서 변환은 확인 전입니다.

## 5.6 다른 팀원이 이어서 일하기

| 항목 | 내용 |
|---|---|
| 실습 ID | `ch05-handoff`, 이어서 `ch05-handoff-record` |
| 지시문 | [prompts/ch05-handoff.txt](prompts/ch05-handoff.txt) |
| 결과 | `work/output/handoff.md`(인수인계 메모 + 발행일을 고친 SNS 초안) |
| 자동 확인 | '2026-10-15'·'EV-BB-1008-CALL'·'확인 필요' |

```bash
python3 run.py run ch05-handoff --workspace work --engine api
python3 run.py run ch05-handoff-record --workspace work --engine api   # 초안 2판을 raw/..._sns-draft-v2.md로 넣고 정리
```

4.2의 초안 원본은 고치지 않고 새 날짜의 원본으로 넣습니다.

## 되돌아갈 자리

- 합성 서비스: [start/services.json](start/services.json), [start/events.json](start/events.json)
- 비교용: [completed/](completed/), 비교용 위키 [completed/studio-merry-wiki/](completed/studio-merry-wiki/)
- 위키 정리가 어긋나면 새 작업 폴더를 4장 끝 위키로 시작: `python3 run.py prepare --workspace work-ch05 --wiki-from ch04`
