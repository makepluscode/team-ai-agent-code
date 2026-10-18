# 8장 독립 실습

합성 입력과 편집 비교 결과(author-reference)입니다. 저자 전건 검수 전이며 실제 모델 응답·실서비스 연결·두 기준 장비 검증을 뜻하지 않습니다.

코드 경로(code/에서 실행):

```sh
uv run team-work prepare --chapter 8 --workspace /tmp/merry-ch08
uv run team-work requests init --workspace /tmp/merry-ch08
uv run team-work requests list --workspace /tmp/merry-ch08
```

지시문 경로: 준비한 prompts/task.md를 헤르메스에 파일로 입력하거나 복사합니다. input/의 시작 자료와 raw/를 읽고 output/에 새 결과를 저장합니다. 준비 시 reference/는 복사하지 않습니다.

복구: 기존 작업 폴더를 보존하고 다른 빈 폴더에 다시 prepare·init합니다. DB를 수동 수정하지 않습니다. 완료 기준은 아래의 장별 확인을 따릅니다.

```sh
uv run team-work requests classify --workspace /tmp/merry-ch08 --request-id REQ-001
```

ANTHROPIC_API_KEY와 TEAM_AGENT_MODEL 설정 뒤 상용 판정을 먼저 사용합니다. 키는 셸/환경 설정으로만 전달합니다. 현재 실제 상용 호출은 미검증입니다. 다음 대안은 편집 예시를 읽고 검사할 뿐 모델 호출 성공이 아닙니다.

```sh
uv run team-work requests classify --workspace /tmp/merry-ch08 --request-id REQ-001 --reference /tmp/merry-ch08/input/classification-reference/REQ-001.json
```

REQ-001~010을 각각 판정합니다. 형식/호출 실패는 확인 필요와 실패RUN을 남기며 상태를 승인·완료로 바꾸지 않습니다. classification-reference/는 입력 요청과 별도 비교용이며 상용 호출에 전달하지 않습니다. 선택 Laya 설치/API/한국어/두 장비 성능은 TODO(검증). 평가60건의 답은 start/ 밖 reference/evaluation-gold.json이며 모델에 전달하지 않습니다. 개발18건으로 조정·동결한 뒤 평가42건을 엽니다. 자동 담당 확정·발송은 없습니다.

판정 결과를 JSON 배열로 별도 저장한 뒤 아래 비교기를 사용합니다. reference-gold의 현재 상태는 저자 전건 검수 전입니다. 제공 정답을 예측값으로 넣는 동작 시험은 모델 품질 검증과 구별합니다.

```sh
uv run team-work requests evaluate --predictions predictions.json --gold examples/requests/ch08/reference/evaluation-gold.json --split evaluation
```

유형·담당후보 집합·긴급도 오류·확인 필요 누락·사람에게 넘긴 비율·자동 판정 오판·호출/결과 누락을 계산합니다. 비용과 시간은 실제 runs를 별도 참조하며 없는 값은 만들지 않습니다.
