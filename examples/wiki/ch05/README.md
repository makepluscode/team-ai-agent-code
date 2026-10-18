# 5장 동료 변경 인계

합성 업무 자료 v1.7. 입력은 start/, 지시문은 prompts/, 편집 비교 결과는 reference/입니다. 앞 장 결과 없이 독립 시작합니다.

## 두 실행 경로

지시문 경로: 준비 후 prompts/ 파일을 헤르메스에 파일 입력하거나 복사합니다. 입력과 출력 경로·확인 기준을 함께 전달합니다. 제공 코드 경로는 아래 명령을 사용합니다. 상용 호출은 환경 변수 ANTHROPIC_API_KEY와 공식 문서로 확인한 TEAM_AGENT_MODEL을 지정합니다. 키를 파일·결과·캡처에 넣지 않습니다.

```sh
uv run team-work prepare --chapter 5 --workspace work/ch05
uv run team-work wiki register --source work/ch05/input/DOC-010_schedule-change.md --workspace work/ch05
uv run team-work wiki propose --workspace work/ch05
uv run team-work wiki apply --proposal work/ch05/output/wiki-proposal.json --confirm --workspace work/ch05
uv run team-work documents generate --task handoff-guide --workspace work/ch05
```

검사: 동료 원본→담당 위키→동료 DOC-007@r2 / EVT-006·DOC-010·15일 날짜/시각·장소 미정 / 충돌 시 중단

편집 비교: `uv run team-work reference --chapter 5`로 위치를 확인하고 실제 output/과 나란히 읽습니다. 실제 응답에는 .run.json이 붙습니다. reference를 모델 응답으로 바꾸지 않습니다.

복구는 RECOVERY.md를 따릅니다.

TODO: 상용 API 실제 호출·Hermes 설치/연계·두 기준 장비는 TODO(검증)
TODO: 온라인 GitHub 인증/초대·skills tap은 TODO(검증). 두 폴더는 로컬 인계 대안입니다.
