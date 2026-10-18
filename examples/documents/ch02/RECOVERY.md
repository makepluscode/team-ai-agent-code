# 복구

기존 폴더를 보존하고 `uv run team-work prepare --chapter 2 --workspace work/ch02-retry`로 새로 시작합니다.

원본 해시 오류는 원본 복사본을 새 폴더에서 다시 읽어 확인합니다. 결과가 있으면 덮어쓰지 않습니다. 확인한 작업 폴더는 `uv run team-work backup --source work/ch02 --destination work/ch02-backup`으로 보관하고 `restore --source work/ch02-backup --destination work/ch02-restored`로 새 폴더에 복구합니다. 위키 적용 전 사본은 output/wiki-before/에 남습니다.
