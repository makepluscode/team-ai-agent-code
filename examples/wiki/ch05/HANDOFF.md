# 두 폴더 인계

1. 5장 시작 자료를 work/curator와 work/member에 각각 준비합니다. 두 폴더는 두 계정 초대 검증이 아닙니다.
2. 자료 담당 원본 input/DOC-010_schedule-change.md를 curator에서 wiki register로 raw/에 등록합니다.
3. curator에서 wiki propose를 실행해 날짜만 확정되고 시각·장소가 미정인지 확인합니다. wiki apply --confirm 뒤 wiki/와 raw/DOC-010을 member에 전달합니다. 수동 복사 때에도 기존 폴더를 백업하고 차이를 검토합니다.
4. member에서 documents generate --task handoff-guide로 결과를 작성합니다. DOC-007@r2, EVT-006, DOC-010@r1이 같은 변경으로 이어지는지 확인합니다.
5. 실제 Git 공유에서는 기존 wiki-sync 스킬의 status/commit/pull/push를 사용하고 고른 파일만 기록합니다. 충돌·거부 시 멈춥니다. 강제 올리기는 하지 않습니다. GitHub 인증·초대와 hermes skills tap은 TODO(검증)입니다.
