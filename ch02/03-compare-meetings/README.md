# 03-compare-meetings: 지난주와 이번 주 회의 비교하기

정리본 가운데 두 주간회의 노트를 헤르메스가 읽고 공통점·변화·제안·미정을 출처와 함께 비교표(DOC-006)로 저장하는 예제입니다. 책 2.3절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch02/03-compare-meetings
hermes chat --query-file prompt.md
uv run check.py
```

헤르메스가 결과를 저장하고 다시 읽어 보여 주면 `/exit`로 대화를 마친 뒤 check.py를 실행합니다.

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 비교 기준과 저장 위치를 담은 지시문 |
| input/ | 02-organize-notes의 정리본과 같은 두 주간회의 노트(합성 자료) |
| expected/DOC-006_comparison.md | 저자가 편집한 비교용 결과. 실제 모델 응답이 아닙니다 |
| check.py | 원본 보존과 결과 저장을 확인하고, 사람이 대조할 줄을 보여 줍니다 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |

앞 예제를 하지 않았어도 이 폴더의 input/만으로 시작할 수 있습니다.
