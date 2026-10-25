# 02-notice-check: 안내문의 자료 경로 확인

매니저가 새 팀원에게 보낼 안내문(input/notice.md)에 적힌 자료 경로 세 개가 팀 자료함(input/shared/)에 실제로 있는지 헤르메스가 하나씩 열어 확인하고, 결과를 표로 저장하는 예제입니다. 내 폴더를 볼 수 없는 보통의 챗봇은 할 수 없고, 파일 도구를 쓰는 에이전트는 할 수 있는 일입니다. 책 1.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch01/02-notice-check
hermes chat --query-file prompt.md
head output/notice-check.md
```

헤르메스가 결과를 저장하고 다시 읽어 보여 주면 `/exit`로 나와 `head`로 파일을 직접 엽니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 헤르메스에 보내는 지시문 |
| input/notice.md | 매니저의 안내문 초안(합성 자료). 경로 세 개 가운데 하나가 실제 위치와 다릅니다 |
| input/shared/ | 팀 자료함 사본. 파일 세 개(team/, tools/, archive/) |
| output/ | 헤르메스가 결과를 저장하는 곳(실행하면 생깁니다) |
| expected/notice-check.md | 편집한 비교용 결과. 실제 모델 응답이 아닙니다 |
| reset.py | 결과 폴더(output/)를 지워 처음부터 다시 하기. ~/.hermes는 바꾸지 않습니다 |

결과 파일을 열어 확인합니다. 3번 경로만 '위치 다름'(실제 위치 shared/archive/notice-retro.md)이고 나머지 두 개는 '정상'이면 됩니다.

## 다시 하기

```bash
uv run reset.py
```
