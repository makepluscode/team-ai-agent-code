월말 마감 기준으로 시작 기록(input/snapshot.json), 월말 비교 자료(input/month-end-snapshot.json),
uv run main.py json의 실행 기록(runs)을 읽어 월말 운영 마감 보고서를 써 줘.
1. 10/19 기록(요청 10·업무 12: 완료 5·진행 2·확인 대기 5)과 10/30 마감 자료(요청 11·업무 13: 완료 6·진행 2·확인 대기 5)의 차이를 비교하고,
   미완료 업무와 기한 초과 업무가 임의로 완료 처리되지 않았는지 확인해 줘.
2. data_kind가 synthetic인 합성 사건과 observed인 실제 실행 기록을 나눠 집계하고, 측정하지 않은 시간·사용량·비용은 null로 둬.
3. uv run main.py restore로 만든 복구 폴더에서 같은 요청·업무 상태가 재현되는지 확인할 항목을 정리해 줘.
output/monthly-ops-report.md에 저장하고 다시 읽어 보여 줘.
