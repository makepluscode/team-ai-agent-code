uv run main.py json을 실행해 requests·classifications·runs·events를 읽고 요청 10건의 판정 기록을 정리해 줘.
요청마다 유형·긴급도·담당 후보·확인 필요 여부와 판정 사건의 event_id를 표로 묶어 요청 처리 현황 DOC-014@r3을 만들어 줘.
헤르메스 판정을 가져온 기록(engine: hermes, data_kind: observed)과 시작 자료의 합성 기록(synthetic)을 구분해 줘.
측정하지 않은 사용량과 비용은 null로 둬. output/doc-014-r3.md에 저장하고 다시 읽어 보여 줘.
