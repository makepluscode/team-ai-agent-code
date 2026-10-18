---
type: criteria
id: inquiry-routing
updated: 2026-10-16
sources: 
  - raw/20261016_TEAM_review-cases.md
---

# 문의 분류와 담당 지정 판단 기준

비교용 결과입니다. 저자가 규칙 파일(AGENTS.md)에 맞춰 작성했으며 모델 응답이 아닙니다.

이번 주 확인 12건 중 판정과 같았던 확인 10건(견적 6, 일정 2, 단순문의 2), 사람이 고친 2건입니다. (출처: raw/20261016_TEAM_review-cases.md)

| 기준 | 종류 | 상태 | 근거 사례 | 반영 위치 | 반영일 | 다시 볼 날 |
|---|---|---|---|---|---|---|
| 랜딩 문구라도 캠페인 메시지를 새로 쓰면 기획이 협업 | 직군 판정 | 후보 | INQ-BB-D06-A: 개발 → 개발(주)+기획(협업) (출처: raw/20261016_TEAM_review-cases.md) | questions.json 2판 후보(role.기획 설명, collaborator 질문) | 확인 필요 | 개발 묶음 재측정 뒤 |
| 단가표에 없는 협업 요청은 담당 직군과 별도로 PM이 확인 | 확인 규칙 | 후보 | INQ-LB-D09-A: 직군 기획 유지, 확인 책임자 PM 추가 (출처: raw/20261016_TEAM_review-cases.md) | rules.json criteria_rules(CRIT-OFFLIST-PM) | 확인 필요 | 확인 필요 |

- 공통점은 원본에서 제안으로만 적혔으므로 두 기준 모두 '후보'입니다. 승인과 적용은 PM이 정합니다. (출처: raw/20261016_TEAM_review-cases.md)
- 담당 직군과 확인 책임자는 따로 적습니다. D09는 직군을 PM으로 바꾼 사례가 아닙니다. (출처: raw/20261016_TEAM_review-cases.md)

관련 결정: [판정 경로](../decisions/20261013_judgment-route.md)
