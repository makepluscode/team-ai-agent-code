# 01-hello-jarvis: 연결 확인·이름 붙이기·메모리·CLI

클로드 연결을 짧은 질문으로 확인하고(책 1.2.4항), 헤르메스의 기본 규칙 파일 SOUL.md에 이름(자비스)과 역할을 적어 자기소개로 적용을 확인합니다(1.2.5항). 이어서 메모리(USER.md·MEMORY.md)에 예제 위치와 보고 선호를 실습용 항목으로 저장하고 새 대화에서 이어지는지 확인한 뒤 지우고(1.4절), 같은 질문을 명령줄과 지시문 파일로 보내 실행 방식을 비교합니다(3.3절 참고 노트).

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch01/01-hello-jarvis
```

1. 연결 확인(1.2.4항): `hermes chat`을 열고 question.md의 질문을 입력합니다. 끝나면 `/exit`.
2. 이름 붙이기(1.2.5항):

```bash
cp --update=none ~/.hermes/SOUL.md ~/.hermes/SOUL.md.orig
cp SOUL.md ~/.hermes/SOUL.md
hermes chat --query-file prompt.md
```

3. 메모리(1.4절): 대화마다 `/exit`로 나온 뒤 다음 명령을 실행합니다.

```bash
hermes chat --query-file remember.md
cat ~/.hermes/memories/USER.md ~/.hermes/memories/MEMORY.md
hermes chat --query-file recall.md
hermes chat --query-file forget.md
cat ~/.hermes/memories/USER.md ~/.hermes/memories/MEMORY.md
```

4. 실행 방식 비교(3.3절 참고 노트의 -Q):

```bash
hermes chat -Q -q "온보딩 자료를 한 장으로 요약할 때 빠뜨리면 안 되는 확인 항목 세 가지를 짧게 알려 줘."
hermes chat -Q --query-file question.md
```

- `cp --update=none`은 백업 파일이 이미 있으면 덮어쓰지 않습니다. 처음 설치한 SOUL.md를 한 번만 보관합니다.
- 다른 이름을 쓰려면 SOUL.md의 '자비스'를 바꾼 뒤 복사합니다. 원래대로 되돌리려면 `cp ~/.hermes/SOUL.md.orig ~/.hermes/SOUL.md`를 실행합니다.
- 메모리는 대화를 시작할 때 읽히므로 저장한 내용은 다음 대화부터 반영됩니다. '기억했다'는 답만 믿지 말고 cat으로 파일을 확인합니다.
- 테스트베드 헤르메스 v0.22.1의 `hermes memory --help`에는 USER.md·MEMORY.md의 모든 기억을 지우는 `reset`이 있습니다. 이 실습에서는 쓰지 않습니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| SOUL.md | 이름·역할·결과 파일 작성 표시를 정하는 기본 규칙 |
| question.md | 연결 상태를 확인하는 짧은 업무 질문(1.2.4항) |
| prompt.md | 자기소개를 요청하는 지시문(1.2.5항) |
| remember.md | 보고 선호(USER.md)와 예제 위치(MEMORY.md)를 '실습용' 항목으로 저장하게 하는 지시문 |
| recall.md | 새 대화에서 기억을 말하고, 경로를 알려 주지 않은 채 1장 점검표를 찾아 기억한 선호대로 보고하게 하는 지시문 |
| forget.md | '실습용' 항목만 지우게 하는 지시문 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기. 헤르메스의 SOUL.md·메모리는 되돌리지 않습니다 |

자기소개에 자비스라는 이름과 매니저의 업무를 돕는다는 역할이 나오면 적용된 것입니다. 이 폴더에 SOUL.md가 있는 것만으로는 적용되지 않습니다. ~/.hermes/SOUL.md로 복사해야 헤르메스가 읽습니다. 메모리에는 API 키·비밀번호·고객 정보와 바뀌는 업무 사실을 넣지 않습니다.
