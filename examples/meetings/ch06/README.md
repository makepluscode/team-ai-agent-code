# 6장 회의 결정

합성 업무 자료 v1.7. 입력은 start/, 지시문은 prompts/, 편집 비교 결과는 reference/입니다. 앞 장 결과 없이 독립 시작합니다.

## 두 실행 경로

지시문 경로: 준비 후 prompts/ 파일을 헤르메스에 파일 입력하거나 복사합니다. 입력과 출력 경로·확인 기준을 함께 전달합니다. 제공 코드 경로는 아래 명령을 사용합니다. 상용 호출은 환경 변수 ANTHROPIC_API_KEY와 공식 문서로 확인한 TEAM_AGENT_MODEL을 지정합니다. 키를 파일·결과·캡처에 넣지 않습니다.

```sh
uv run team-work prepare --chapter 6 --workspace work/ch06
uv run team-work documents generate --task meeting-notes --workspace work/ch06
uv run team-work wiki register --source work/ch06/output/DOC-012_meeting-notes.md --workspace work/ch06
uv run team-work wiki propose --workspace work/ch06
uv run team-work wiki apply --proposal work/ch06/output/wiki-proposal.json --confirm --workspace work/ch06
```

검사: 15일 10:00 회의실 A / 12일 취소/14일 미채택 / TASK-009/TASK-002·담당·기한 / 원음 대조가 없으면 전사·음원 검증 미완료

편집 비교: `uv run team-work reference --chapter 6`로 위치를 확인하고 실제 output/과 나란히 읽습니다. 실제 응답에는 .run.json이 붙습니다. reference를 모델 응답으로 바꾸지 않습니다.

복구는 RECOVERY.md를 따릅니다.

TODO: 상용 API 실제 호출·Hermes 설치/연계·두 기준 장비는 TODO(검증)
TODO: 음원 미제작·청취/전사 미실행. 제공 합성 대본으로 결정 추출 대안만 진행합니다.
