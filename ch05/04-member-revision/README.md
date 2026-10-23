# 04-member-revision: 위키를 받은 동료의 결과 수정

매니저의 wiki-curator가 갱신한 위키를 받은 동료(M02)의 폴더입니다. 헤르메스가 위키와 변경 원본을 근거로 온보딩 가이드
2번째 버전(DOC-007@r2)을 만듭니다. 이 단계까지 끝나야 동료 인계가 완료됩니다. 책 5.4절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch05/04-member-revision
uv run main.py receive
hermes chat --query-file prompt.md
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| wiki/ | 변경 메모가 반영된 위키(5.3절 결과와 같은 비교용 예시) |
| raw/DOC-010_schedule-change.md | 변경 메모 원본 |
| input/DOC-007_onboarding-guide.r1.md | 수정할 온보딩 가이드 1번째 버전 |
| prompt.md | 가이드 수정 지시문 |
| expected/DOC-007_onboarding-guide.r2.md | 비교용 2번째 버전 |
| check.py | 원본 보존·결과 저장 확인 |
| main.py | 단계 receive. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


receive는 같은 장 폴더의 03-change-memo를 마친 뒤 실행해 실제 결과를 넘겨받는 인계입니다. 03을 건너뛰었다면 receive 없이 미리 넣어 둔 위키(03 완료 상태의 비교용 예시)로 연습할 수 있지만 그것은 인계 확인이 아닙니다. GitHub으로 공유했다면 동료 폴더(~/studio-merry-wiki-member)에서 '위키 동기화해 줘'로 받은 뒤 같은 지시문을 씁니다.
