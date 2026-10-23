# 02-compare-paths: 판정 경로 비교

개발용 18건으로 기준을 맞춘 뒤 평가용 42건을 헤르메스로 판정하고, main.py가 저자 기준 정답과 비교해 유형 정확도·담당 후보 일치·
긴급도 오류·확인 필요 누락·사람에게 넘긴 비율을 계산합니다. 선택 로컬 판정(Laya)과의 비교는 TODO(검증)입니다. 책 8.4절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch08/02-compare-paths
hermes chat --query-file prompt.md
uv run main.py evaluate
uv run check.py
```

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 받은 처음 상태로 되돌린 뒤 실행 방법을 다시 따라 합니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| input/evaluation/ | 개발용 18건·평가용 42건(합성, 정답 없음) |
| input/routing-criteria.json | 판정 기준 |
| prompt.md | 개발·평가 판정 지시문 |
| expected/evaluation-gold.json | 저자 기준 정답(저자 전건 검수 전). 헤르메스에 주지 않음 |
| check.py | 원본 보존·판정 저장 확인 |
| main.py | 단계 evaluate. 인자 없이 실행하면 할 일과 단계를 안내 |
| reset.py | 예제 폴더를 받은 처음 상태로 되돌리기(다시 할 때) |


evaluate는 main.py 위치를 기준으로 상대 경로를 읽으므로 이 폴더에서 실행합니다.
