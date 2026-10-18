# 3장 반복 업무와 개인 예약

합성 업무 자료 v1.7. 입력은 start/, 지시문은 prompts/, 편집 비교 결과는 reference/입니다. 앞 장 결과 없이 독립 시작합니다.

## 두 실행 경로

지시문 경로: 준비 후 prompts/ 파일을 헤르메스에 파일 입력하거나 복사합니다. 입력과 출력 경로·확인 기준을 함께 전달합니다. 제공 코드 경로는 아래 명령을 사용합니다. 상용 호출은 환경 변수 ANTHROPIC_API_KEY와 공식 문서로 확인한 TEAM_AGENT_MODEL을 지정합니다. 키를 파일·결과·캡처에 넣지 않습니다.

```sh
uv run team-work prepare --chapter 3 --workspace work/ch03
uv run team-work documents generate --task onboarding-guide --workspace work/ch03
uv run team-work documents generate --task improvement-memo --workspace work/ch03
uv run team-work documents generate --task weekly-report --workspace work/ch03
uv run team-work schedule create --at 2026-10-09T17:00:00+09:00 --workspace work/ch03
uv run team-work schedule status --workspace work/ch03
uv run team-work schedule run-due --confirm --workspace work/ch03
uv run team-work schedule pause --workspace work/ch03
```

검사: DOC-007/008/009 사실·제안·미정 / 관측 완료 4건·미입력 구별 / 개인 스킬 하나·예약 하나·실제 실행/다음 실행 구별

편집 비교: `uv run team-work reference --chapter 3`로 위치를 확인하고 실제 output/과 나란히 읽습니다. 실제 응답에는 .run.json이 붙습니다. reference를 모델 응답으로 바꾸지 않습니다.

복구는 RECOVERY.md를 따릅니다.

TODO: 상용 API 실제 호출·Hermes 설치/연계·두 기준 장비는 TODO(검증)
TODO: 제공 개인 예약은 run-due를 직접 호출하는 실행기입니다. 백그라운드 서비스나 Hermes 예약 등록 성공을 뜻하지 않습니다.
