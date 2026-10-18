# 8장 견적 초안과 사람의 확인

『팀 AI 에이전트 실전』 8장의 실습 안내입니다. 단가표로 견적 초안을 계산하고, 사람이 확인하는 경계를 세우고, 사람의 승인·수정을 이력으로 남긴 뒤, 고친 사례를 위키의 판단 기준 페이지로 쌓아 다음 판정에 반영합니다.

- 원고: `content/ch08_quote-review_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/)(단가표·견적 요청·질문 2판·규칙 2판), 실습 정의 [tasks.json](tasks.json), 위키 원본 [wiki-raw/](wiki-raw/)
- 실행기: [../part3.py](../part3.py)
- 8장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)(판단 기준 페이지 `wiki/criteria/inquiry-routing.md`)

> 확인 범위: 견적 계산·상태·사람 확인 기록·확인 사례 원본은 제공 코드로, 판단 기준 페이지 정리와 D06 반영 전후 판정은 상용 API로 2026-10-15에 실행했습니다. 정답 견적 전체 묶음과 기록 복구는 확인 전입니다. 단가·규칙은 합성 값입니다.

7장의 `work-part03` 작업 폴더를 이어서 씁니다(`database`까지 마친 상태).

## 8.1 견적 초안

```bash
python3 part3.py quote --workspace work-part03 --inquiry INQ-BB-D01-A   # 200,000×2 → 공급가 400,000 + 세금 40,000 = 440,000원
python3 part3.py quote --workspace work-part03 --inquiry INQ-BB-D06-C   # 여러 상품: 랜딩 문구 2 + 게시물 2 = 1,540,000원(고액 확인)
python3 part3.py quote --workspace work-part03 --inquiry INQ-DP-D08-A   # 수량 미정 → 금액 없음
python3 part3.py quote --workspace work-part03 --inquiry INQ-LB-D09-A   # 단가표 밖 → 금액 없음
```

단가는 조회 전용 DB에서 읽고 Decimal·ROUND_HALF_UP으로 계산합니다. `send_allowed`는 항상 false, 상태는 review_required입니다. 여러 상품 견적은 [start/quote-requests.json](start/quote-requests.json)의 `items` 목록으로 씁니다.

## 8.2 사람이 확인하는 경계

설명용 규칙([../ch07/start/rules.json](../ch07/start/rules.json)): 신뢰도 0.85, 계약 중단 0.5, 고액 1,000,000원 이상. `criteria_rules`에는 8.4에서 정리할 확인 규칙이 '후보' 상태로 들어 있고, `status`가 '적용'인 규칙만 라우팅에 쓰입니다.

## 8.3 상태 기록과 사람의 확인

```bash
for id in INQ-BB-D01-A INQ-BB-D06-A INQ-LB-D09-A; do
  python3 part3.py decide --workspace work-part03 --inquiry $id --transport api   # 7장에서 했으면 생략
  python3 part3.py route  --workspace work-part03 --inquiry $id
  python3 part3.py quote  --workspace work-part03 --inquiry $id
  python3 part3.py state  --workspace work-part03 --inquiry $id
done
python3 part3.py review --workspace work-part03 --inquiry INQ-BB-D01-A --decision approved --reason "단가표와 수량이 요청과 일치"
python3 part3.py review --workspace work-part03 --inquiry INQ-BB-D06-A --decision changed --set collaborator=기획 \
  --reason "랜딩 문구 교체에 캠페인 메시지가 새로 들어간다"
python3 part3.py review --workspace work-part03 --inquiry INQ-LB-D09-A --decision changed --set confirm_owner=PM \
  --reason "인플루언서 협업은 단가표 밖이라 예산·계약 조율이 먼저 필요하다"
```

`state`는 라우팅 결과에 견적 파일 경로와 이력 v1(모델 판정)을 붙여 proposed 또는 review_pending으로 저장합니다. `review`는 이유가 없으면 거부하고, 이력 v2(사람·이유·바뀐 항목)를 더합니다. 결정은 approved·rejected·revise_requested·changed입니다. 담당 직군(`role`)과 확인 책임자(`confirm_owner`)는 따로 고칩니다.

## 8.4 판단 기준을 위키에

```bash
python3 part3.py review-cases --workspace work-part03                          # output/review-cases.md (확인 사례 원본)
python3 part3.py wiki ch08-criteria-record --workspace work-part03 --engine api
```

`review-cases`는 이번 주에 사람이 확인한 건수(reviewed)·고친 건수(changed)·고친 사례·판정과 같았던 건수를 원본 형식으로 씁니다. 문의 원문과 연락처는 넣지 않습니다. 공통점은 PM이 직접 적습니다. 원고의 예시 원본은 [wiki-raw/20261016_TEAM_review-cases.md](wiki-raw/20261016_TEAM_review-cases.md)입니다.

위키 정리는 규칙 파일에 판단 기준 페이지 종류를 한 줄 더한 뒤 `wiki/criteria/inquiry-routing.md`를 만듭니다. 자동 검사: 두 사례 ID와 '후보' 상태, 규칙 파일의 `wiki/criteria/`.

### 반영 전후 비교(이 장의 마지막 결과)

질문 2판([start/questions.v2.json](start/questions.v2.json))은 기획 직군 설명에 한 줄을 더하고 '협업 직군' 질문을 둡니다. 규칙 2판([start/rules.v2.json](start/rules.v2.json))은 '단가표 밖 협업은 PM 확인'을 적용 상태로 둡니다. 결과는 `<ID>.v2.json`으로 따로 저장해 1판과 나란히 봅니다.

```bash
python3 part3.py decide --workspace work-part03 --inquiry INQ-BB-D06-A --transport api --version v2
python3 part3.py route  --workspace work-part03 --inquiry INQ-BB-D06-A --version v2      # 협업 직군 확인 이유
python3 part3.py decide --workspace work-part03 --inquiry INQ-LB-D09-A --transport api --version v2
python3 part3.py route  --workspace work-part03 --inquiry INQ-LB-D09-A --version v2      # confirm_owner PM, 직군은 그대로
python3 part3.py decide-all --workspace work-part03 --transport api --version v2          # 개발 묶음 다시 재기
python3 part3.py compare --workspace work-part03 --dev --version v2
```

새 판은 개발 묶음으로 다시 잰 뒤에만 기본값으로 바꿉니다. 평가 묶음 결과를 보며 기준을 고치지 않습니다.

## 되돌아갈 자리

- 이전 판 질문·규칙: [../ch07/start/questions.json](../ch07/start/questions.json), [../ch07/start/rules.json](../ch07/start/rules.json)
- 코드: [../part3.py](../part3.py)의 `estimate`·`state_record`·`review`·`review_cases`·`routing`의 `criteria_rules`
