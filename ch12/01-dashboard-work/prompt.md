M02가 요청한 다음 안내 수정 건(input/dashboard-request.json의 REQ-011)을 대시보드에 표시할 레코드로 정리해 줘.
1. 요청 REQ-011, 요청자 M02, 연결 업무 TASK-013. 이전 완료 업무 TASK-002는 related_task_id로만 참조해 줘.
2. 위키의 최신 온보딩 가이드(DOC-007@r3), 회의 결정(DOC-012@r1), 사람 확인 기준(DOC-013@r1)을 근거(source_refs)로 연결해 줘.
3. 처리 주체(actor_id)와 처리 경로 배지(AI 챗봇 초안 생성, M01 최종 확인 예정)를 구분하고, 업무 상태는 완료가 아니라 진행으로 적어
   output/evt-018-instruct.json에 저장해 줘. DB는 고치지 마.
