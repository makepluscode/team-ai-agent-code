회의 음원(input/MTG-001_meeting.mp3)을 내 컴퓨터에서 로컬로 전사해 줘.
1. 이 폴더에서 `uv run --extra transcription main.py transcribe input/MTG-001_meeting.mp3`를 실행해.
   처음에는 전사 프로그램과 모델을 내려받아 시간이 걸려. 오류가 나면 멈추고 오류를 그대로 보여 줘.
2. 끝나면 output/transcript.json의 구간을 시작 시각과 함께 표로 보여 줘.
3. 기준 전사문(input/DOC-011_transcript-fallback.md)과 다르게 적힌 낱말을 '구간 | 전사 결과 | 기준 전사문' 표로 보여 줘.
   날짜·시각·장소·이름이 다른 곳은 따로 표시해 줘.
전사 결과와 입력 파일은 고치지 마.
