"""명령 결과(dict·list)를 사람이 읽기 쉬운 줄로 바꾼다.

입력: CLI 명령이 돌려준 결과(JSON으로 바꿀 수 있는 값)
출력: 한국어 이름을 붙인 들여쓰기 텍스트. 저장된 모든 필드는 예제의 json 단계(JSON 출력)로 본다.
실행: 예제의 main.py가 환경 변수 TEAM_WORK_TEXT=1을 주면 cli.main이 이 형식으로 출력한다.
"""

# 자주 나오는 필드의 한국어 이름. 없는 이름은 원래 키를 그대로 쓴다
LABELS = {
    "applied": "적용한 파일 수", "backup": "백업 위치", "proposal": "제안 기록", "files": "적용한 파일",
    "draft_kept": "보관한 변경안", "next": "다음", "registered": "등록한 원본", "sha256": "해시",
    "at": "검사 시각", "timezone": "시간대", "working_hours": "업무시간 안", "next_open": "다음 업무 시작",
    "holidays_source": "공휴일 기준", "query_id": "질문", "kind": "종류", "answer": "답", "sources": "출처",
    "document_ref": "문서", "revision": "문서 버전", "effective_at": "적용 시각", "state": "상태",
    "engine": "조회 방식", "questions": "질문 수", "failures": "불일치", "ok": "통과", "scope": "범위",
    "review_id": "검토", "reviewer_id": "검토자", "task_id": "업무", "request_id": "요청", "reason": "이유",
    "before_ref": "수정 전", "after_ref": "수정 후", "source_refs": "근거", "actor_id": "처리자",
    "owner_id": "담당", "status": "상태", "event_id": "사건 기록", "before": "이전", "after": "이후",
    "background_schedule_registered": "헤르메스 백그라운드 예약 등록", "mail_connection": "메일 연결",
    "received_from": "받은 곳", "model_call": "모델 호출", "output_ref": "결과 파일", "restored": "복구 위치", "data_kind": "자료 종류",
}


def _scalar(value):
    if value is True:
        return "예"
    if value is False:
        return "아니요"
    if value is None:
        return "-"
    return str(value)


def readable(value, indent=0):
    pad = "  " * indent
    lines = []
    if isinstance(value, dict):
        for key, item in value.items():
            label = LABELS.get(key, key)
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{pad}{label}:")
                lines.append(readable(item, indent + 1))
            else:
                lines.append(f"{pad}{label}: {_scalar(item) if item != [] else '없음'}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(readable(item, indent + 1))
            else:
                lines.append(f"{pad}- {_scalar(item)}")
    else:
        lines.append(pad + _scalar(value))
    return "\n".join(line for line in lines if line)
