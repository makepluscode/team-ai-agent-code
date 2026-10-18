input/internal-requests.json의 내부 요청 8건과 input/members.json 역할 명부를 읽어 줘.
요청마다 request_id, source_kind, received_at, requester_id, body, source_ref 여섯 항목이 있는지 확인해 줘.
본문에 기한이 명시된 경우에만 due_at을 적고, 기한이 없으면 추정하지 말고 null로 남겨 줘.
원문 내용이 같은 중복 입력이 있으면 새 요청 번호로 세지 말고 기존 request_id에 중복 표시만 남겨 줘.
기존 업무(TASK-001, TASK-002)와 이어지는 요청은 해당 task_id를 연결해 줘.
담당자는 미리 정하지 말고 접수 목록을 output/requests-internal.json으로 저장해 줘. 입력 파일은 수정하지 마.
