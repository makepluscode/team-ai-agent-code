분류 기준을 개발용 자료로 맞춘 뒤 평가용 자료를 판정해 줘.

        1. input/routing-criteria.json과 input/members.json을 읽어 줘.
        2. input/evaluation/development.json의 6상황 18건(정중한 요청·짧은 요청·구어체)을 먼저 판정하고,
           같은 상황(situation_id)의 세 표현에 같은 유형과 담당 후보가 나오는지 확인해 줘.
        3. 기준을 고정한 뒤 input/evaluation/evaluation.json의 14상황 42건을 판정해
           output/predictions.json에 요청 ID별 판정의 목록(JSON 배열)으로 저장해 줘. 항목마다 request_id를 넣어 줘.
        4. expected/는 정답이니 절대 읽지 마. 측정하지 않은 시간·비용은 지어내지 마.

판정 파일 형식(JSON 객체 하나):
{"type": "자료 확인 | 문서 작성/수정 | 일정 조정 | 도구 문제 | 기타/복합",
 "owner_candidates": ["M01"~"M05" 가운데 명부 ID],
 "urgency": "낮음 | 보통 | 높음",
 "needs_confirmation": true 또는 false,
 "evidence": "요청 본문에서 그대로 복사한 문장 하나",
 "confirmation_reason": "확인이 필요한 이유(필요 없으면 빈 문자열)"}
