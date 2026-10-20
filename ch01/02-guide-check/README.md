# 02-guide-check: 온보딩 안내문의 자료 경로 점검

매니저가 새 팀원에게 보낼 안내문 초안(DOC-015)에 적힌 자료 경로 5개를 헤르메스가 팀 자료함(input/shared/)에서 실제로 확인하고, 일정·장소를 온보딩 자료 원본(DOC-001)과 대조해 점검표(DOC-005)로 저장하는 예제입니다. 파일 도구를 연결하지 않은 보통의 채팅은 내 폴더를 볼 수 없어 할 수 없고, 파일 도구를 쓰는 에이전트는 할 수 있는 일입니다. 책 1.3절에 대응합니다.

## 실행 방법

```bash
mkdir -p ~/agent-work
cp -r --update=none ~/team-ai-agent/code/ch01 ~/agent-work/
cd ~/agent-work/ch01/02-guide-check
hermes chat --query-file prompt.md
uv run check.py
```

`hermes chat --query-file`은 prompt.md를 첫 요청으로 보내고 대화를 이어 갑니다. 점검표를 확인한 뒤 `/exit`로 나옵니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 헤르메스에 보내는 지시문 |
| input/DOC-015_notice-draft.md | 매니저의 안내문 초안(합성 자료). 일부러 오류를 넣었습니다 |
| input/DOC-001_onboarding.md | 온보딩 자료 원본(잠정 일정·미정 장소) |
| input/shared/ | 팀 자료함 사본. 옛 버전·다른 위치·없는 파일이 섞여 있습니다 |
| output/ | 헤르메스가 점검표를 저장하는 곳(실행하면 생깁니다) |
| expected/DOC-005_guide-check.md | 저자가 편집한 비교용 점검표. 실제 모델 응답이 아닙니다 |
| check.py | 원본·자료함 보존과 결과 저장을 확인하고, 경로마다 저자가 확인한 상태와 점검표의 줄을 나란히 보여 줍니다 |

check.py의 EXPECTED에 경로마다 저자가 확인한 상태가 있습니다(정상 2, 옛 버전 1, 위치 다름 1, 없음 1). 점검표의 문장이 맞는지는 사람이 판단합니다.

## 다시 하기

기존 사본은 그대로 두고 새 이름으로 다시 복사합니다.

```bash
cp -r ~/team-ai-agent/code/ch01 ~/agent-work/ch01-retry
```
