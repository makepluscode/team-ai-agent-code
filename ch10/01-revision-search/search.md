input/queries.json의 질문마다 답하기 전에 근거 위치 목록을 만들어 줘.
1. wiki/index.md와 wiki/log.md에서 관련 위키 페이지 경로를 찾는다.
2. 위키 페이지(guides/onboarding.md, decisions/onboarding.md, criteria/review.md)에서 현재 유효한 절과 source_refs를 찾는다.
3. source_refs의 문서 ID·버전(예: DOC-007@r3, DOC-012#decision-01)을 raw/의 원본 파일 경로와 연결한다.
4. 대체·취소된 버전은 현재 근거에서 빼고 이력 참고로만 분리한다.
질문별 위키 경로·절·원본 문서 ID와 버전을 output/search-hits.json으로 저장해 줘. 답변은 아직 쓰지 마.
