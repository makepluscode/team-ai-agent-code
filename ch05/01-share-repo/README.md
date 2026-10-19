# 01-share-repo: 팀 위키 저장소 준비

4장에서 정리한 로컬 위키를 GitHub 비공개 저장소로 올릴 준비를 하는 예제입니다. 헤르메스가 로그인 상태와 제외 목록(.gitignore)을
확인하고, 사람이 올라갈 파일 목록을 확인한 뒤 저장소를 만듭니다. GitHub 계정과 gh 로그인은 부록 B를 따릅니다. 책 5.1절에 대응합니다.

## 실행 방법

```bash
mkdir -p ~/agent-work && cp -r --update=none ~/team-ai-agent/code/ch05 ~/agent-work/
cp -r ~/agent-work/ch05/01-share-repo ~/studio-merry-wiki
cd ~/studio-merry-wiki
hermes chat --query-file prompt.md
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| AGENTS.md | 위키 정리 규칙 |
| .gitignore | 공유하지 않을 파일 목록 |
| raw/·wiki/ | 4장까지 정리한 원본과 위키 |
| prompt.md | 로그인·제외 목록 확인과 저장소 준비 지시문 |
| check.py | 원본 보존과 제외 목록 확인 |


실제 GitHub 저장소 생성과 올리기는 헤르메스가 gh·git으로 실행합니다. v1.7 예제로 저장소를 새로 만드는 전 과정은 두 기준 장비에서 TODO(검증)입니다.
GitHub을 쓸 수 없으면 이 폴더를 그대로 두고 5.3~5.4절의 두 예제 폴더로 인계를 연습합니다.
