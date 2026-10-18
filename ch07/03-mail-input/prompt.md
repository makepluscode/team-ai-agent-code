input/optional-mail.json 안의 외부 메일 자료 2건을 읽어 줘.
외부 발신자는 requester_id를 external-01, external-02로 적고, 실제 이메일 주소나 서명은 본문 요약에 덧붙이지 마.
원문 참조(source_ref)에는 실제로 읽은 제공 파일의 요청 위치를 남겨 줘. 없는 스레드 ID는 만들지 마.
uv run main.py json의 기록과 합쳐 전체 10건 목록을 output/requests-all.json으로 저장해 줘.
답장 발송이나 개인 메일 전달은 하지 마. 입력 파일은 수정하지 마.
