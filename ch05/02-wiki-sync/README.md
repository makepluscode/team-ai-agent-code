# 02-wiki-sync: 위키 동기화 스킬

팀 위키 저장소에 들어갈 위키 동기화 스킬(skills/wiki-sync)입니다. 바뀐 파일을 사람이 고른 것만 기록하고, 충돌·거부에서는 멈추며,
강제로 올리지 않습니다. 책 5.2절에 대응합니다. 이 폴더의 skills/를 5.1절에서 만든 위키 저장소에 복사해 함께 올립니다.

## 실행 방법

```bash
cp -r ~/agent-work/ch05/02-wiki-sync/skills ~/studio-merry-wiki/
cd ~/studio-merry-wiki
hermes skills tap add <내 GitHub 계정>/studio-merry-wiki
hermes skills install <내 GitHub 계정>/studio-merry-wiki/skills/wiki-sync
uv run skills/wiki-sync/scripts/wiki_sync.py status
hermes chat --query-file ~/agent-work/ch05/02-wiki-sync/prompt.md
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| skills/wiki-sync/SKILL.md | 동기화 절차(헤르메스가 읽는 스킬) |
| skills/wiki-sync/scripts/wiki_sync.py | status·commit·pull·push를 나눠 처리하는 표준 라이브러리 스크립트 |
| prompt.md | '위키 동기화해 줘' 지시문 |
| check.py | 원본 보존과 스킬 파일 확인 |
