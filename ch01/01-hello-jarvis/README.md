# 01-hello-jarvis: 헤르메스에 이름 붙이기

헤르메스의 기본 규칙 파일 SOUL.md에 이름(자비스)과 역할을 적고 자기소개로 적용을 확인하는 예제입니다. 책 1.3.1항에 대응합니다.

## 실행 방법

```bash
mkdir -p ~/agent-work
cp -r ~/team-ai-agent/code/ch01 ~/agent-work/ch01
cd ~/agent-work/ch01/01-hello-jarvis
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig
cp SOUL.md ~/.hermes/SOUL.md
hermes chat --query-file prompt.md
```

- `cp --update=none`은 백업 파일이 이미 있으면 덮어쓰지 않습니다. 처음 설치한 SOUL.md를 한 번만 보관합니다.
- 다른 이름을 쓰려면 SOUL.md의 '자비스'를 바꾼 뒤 복사합니다.
- 원래대로 되돌리려면 `cp ~/.hermes/SOUL.md.orig ~/.hermes/SOUL.md`를 실행합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| SOUL.md | 이름·역할·결과 파일 작성 표시를 정하는 기본 규칙 |
| prompt.md | 자기소개를 요청하는 지시문 |
| question.md | 연결 상태를 확인하는 짧은 업무 질문 |

자기소개에 자비스라는 이름과 매니저의 업무를 돕는다는 역할이 나오면 적용된 것입니다. 이 폴더에 SOUL.md가 있는 것만으로는 적용되지 않습니다. ~/.hermes/SOUL.md로 복사해야 헤르메스가 읽습니다.
