# 03-source-query: 위키 출처 조회

4.3절에서 만든 것과 같은 위키 페이지가 들어 있는 폴더입니다. 헤르메스에 짧은 질문 세 개를 보내 위키 경로와 원본 출처가
함께 답에 붙는지, 잠정·미정·미입력이 유지되는지 확인합니다. 책 4.4절에 대응합니다.

## 실행 방법

```bash
cd ~/agent-work/ch04/03-source-query
hermes chat --query-file prompt.md
uv run main.py search 잠정
uv run check.py
```

## 폴더 구성

| 파일 | 역할 |
|---|---|
| wiki/ | 4.3절 결과와 같은 위키(비교용 편집 예시) |
| raw/ | 초기 원본과 근거 묶음 |
| prompt.md | 질문 세 개와 저장 위치 |
| main.py | search: 검색어가 있는 위키 줄 찾기 |
| expected/ch04-query-check.md | 비교용 답변 |
| check.py | 원본 보존·답변 저장 확인 |
