# 01-weekly-report: 회의 노트·업무 노트로 주간 보고 쓰기

2장에서 정리한 회의 노트·업무 노트·대화 기록 8개로 주간 보고(DOC-009)를 만드는 예제입니다. 같은 일을 여러 자료에서 다시 언급해도 항목키로 한 번만 세고, 상태가 비어 있는 일과 회신 대기인 일을 확인할 점으로 남깁니다. 책 3.1절에 대응합니다.

## 실행 방법

```bash
cd ~/team-ai-agent/code/ch03/01-weekly-report
hermes chat --query-file prompt.md
cat output/DOC-009_weekly-report.r1.md
```

헤르메스가 결과를 저장하고 다시 읽어 보여 주면 `/exit`로 대화를 마친 뒤 결과 파일을 엽니다.

처음부터 다시 할 때는 이 폴더에서 `uv run reset.py`를 실행해 결과 폴더(output/)를 지운 뒤 실행 방법을 다시 따라 합니다. 헤르메스 설정(~/.hermes)은 바뀌지 않습니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| prompt.md | 집계 규칙과 저장 위치를 담은 지시문 |
| input/organized/ | 2장 정리본과 같은 텍스트 자료 8개(사진·확인 필요 파일 제외) |
| input/DOC-004_weekly-meetings.md | 읽을 파일 목록과 집계 원칙(주간 보고 입력 묶음) |
| input/snapshot.json | 관측 기간과 고정된 관측 기준 시각 |
| expected/DOC-009_weekly-report.r1.md | 편집한 비교용 결과(관측 완료 4건) |
| reset.py | 결과 폴더(output/)를 지워 처음부터 다시 하기. ~/.hermes는 바꾸지 않습니다 |

## 확인할 것

결과 파일을 열어 원본(input/)과 대조합니다.

- 관측 기준 시각이 input/snapshot.json의 값 그대로인가
- 완료가 항목키 ITEM-001~004의 네 건이고, 대화의 재언급을 다시 세지 않았는가
- ITEM-005·006이 완료가 아니라 제안·상태 미기재로 남았는가
- 보고 업무 TASK-001이 '확인 대기'인가
