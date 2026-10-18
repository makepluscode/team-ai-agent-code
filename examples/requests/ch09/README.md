# 9장 독립 실습

합성 입력과 편집 비교 결과(author-reference)입니다. 저자 전건 검수 전이며 실제 모델 응답·실서비스 연결·두 기준 장비 검증을 뜻하지 않습니다.

코드 경로(code/에서 실행):

```sh
uv run team-work prepare --chapter 9 --workspace /tmp/merry-ch09
uv run team-work requests init --workspace /tmp/merry-ch09
uv run team-work requests list --workspace /tmp/merry-ch09
```

지시문 경로: 준비한 prompts/task.md를 헤르메스에 파일로 입력하거나 복사합니다. input/의 시작 자료와 raw/를 읽고 output/에 새 결과를 저장합니다. 준비 시 reference/는 복사하지 않습니다.

복구: 기존 작업 폴더를 보존하고 다른 빈 폴더에 다시 prepare·init합니다. DB를 수동 수정하지 않습니다. 완료 기준은 아래의 장별 확인을 따릅니다.

```sh
uv run team-work requests review --workspace /tmp/merry-ch09 --input /tmp/merry-ch09/input/reviews/REV-001.json --actor M01 --human-confirmed
```

사람이 수정본과 근거를 확인한 뒤 REV-001~006을 각각 적용합니다. REV-004는 M05, 나머지는 M01 검토입니다. input/review-corrections/는 편집 수정 예시이며 자동 모델 결과가 아닙니다. review는 output/에 예시를 보존하고 사건·검토 기록을 남깁니다. 최종 확인 뒤 TASK-001·002를 완료로 변경합니다. TASK-006은 진행→확인 대기→완료(M02 확인)를 별도로 기록합니다. REV-003은 기존 TASK-009를 부모 TASK-008에 연결하고 접근 문제 TASK-010만 추가합니다. 완료5·진행2·확인 대기5가 비교 기준입니다. DOC-013 기준은 검토6건 뒤 output/에 생성합니다. 증상·외부 공유·불충분 요청은 확인 대기 유지합니다.
