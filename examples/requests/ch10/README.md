# 10장 독립 실습

합성 입력과 편집 비교 결과(author-reference)입니다. 저자 전건 검수 전이며 실제 모델 응답·실서비스 연결·두 기준 장비 검증을 뜻하지 않습니다.

코드 경로(code/에서 실행):

```sh
uv run team-work prepare --chapter 10 --workspace /tmp/merry-ch10
uv run team-work requests init --workspace /tmp/merry-ch10
uv run team-work requests list --workspace /tmp/merry-ch10
```

지시문 경로: 준비한 prompts/task.md를 헤르메스에 파일로 입력하거나 복사합니다. input/의 시작 자료와 raw/를 읽고 output/에 새 결과를 저장합니다. 준비 시 reference/는 복사하지 않습니다.

복구: 기존 작업 폴더를 보존하고 다른 빈 폴더에 다시 prepare·init합니다. DB를 수동 수정하지 않습니다. 완료 기준은 아래의 장별 확인을 따릅니다.

```sh
uv run team-work wiki-qa --workspace /tmp/merry-ch10 --query-id Q01
uv run team-work wiki-qa --workspace /tmp/merry-ch10 --check
```

질문20개·원본 위치·현재/과거/미정/충돌/취소를 검사합니다. 제공 경로는 구조화 출처 조회입니다. 상용 생성 문장 품질이나 자유 질문 검색 품질을 측정한 결과가 아닙니다. 원본 파일·앵커가 없으면 오류로 멈춥니다. 새 질문은 input/queries.json에 key·기준 시각을 등록합니다.
