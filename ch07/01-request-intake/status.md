uv run main.py json을 실행해 기록 DB의 requests·tasks·events·runs 배열을 읽어 줘.
독립 시작의 합성 기록(input/snapshot.json)과 이번 접수로 생긴 기록을 구별해 줘.
내부 요청 8건의 request_id, task_id, 요청자, 접수 시각, 현재 상태, 원문 경로를 요청 처리 현황(DOC-014@r1) 표로 정리해 줘.
실행 기록(runs)이 있으면 업무 ID와 실행 시도(run_id)를 구분해 성공·실패 건수를 집계해 줘.
측정하지 않은 사용량(usage)이나 비용(cost)은 0으로 바꾸지 말고 null 그대로 적어 줘.
결과는 output/doc-014-r1.md에 저장하고 다시 읽어 보여 줘. DB나 입력 파일은 고치지 마.
