# 개인 주간 보고 스킬과 예약

스킬 버전은 1.7.0입니다. SKILL.md는 주간 활동표의 관측값과 미입력·미확인을 구별하는 절차이며, schedule.example.json은 미등록 설정 예시입니다. 같은 버전의 파일을 3장 독립 시작 자료와 5장 공유 스킬 스냅샷에 포함했습니다. 스냅샷을 바꾸면 이 원본과 버전·내용을 대조합니다.

```sh
uv run team-work prepare --chapter 3 --workspace work/ch03
uv run team-work schedule create --workspace work/ch03 --at 2026-10-09T17:00:00+09:00
uv run team-work schedule status --workspace work/ch03
uv run team-work schedule run-due --workspace work/ch03 --confirm
uv run team-work schedule pause --workspace work/ch03
```

run-due는 직접 호출하는 제공 실행기입니다. 상용 생성 환경을 설정한 뒤 실제 응답을 output/scheduled-1/에 저장하며 같은 예약의 중복 실행은 거부합니다. 수동으로 만든 보고를 보존합니다. 예약 파일 생성·스킬 파일 제공은 Hermes 스킬 설치나 백그라운드 예약 등록 성공을 뜻하지 않습니다. 해당 연결과 두 기준 장비는 TODO(검증)입니다.
