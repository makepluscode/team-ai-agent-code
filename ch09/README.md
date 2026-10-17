# 9장 회의 자동화

『팀 AI 에이전트 실전』 9장의 실습 안내입니다. 회의 녹음을 로컬에서 전사하고(Whisper), 상용 AI로 결정·할 일을 추출하고, 사람이 확인한 회의록과 개인정보를 지운 전사문을 위키 원본으로 넣어 결정 페이지를 만듭니다.

- 원고: `content/ch09_meeting-automation_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/)(회의 정보·대본·용어표·1분 합성 음원), 지시문 [prompts/ch09-extract.txt](prompts/ch09-extract.txt), 비교용 [completed/](completed/)(전사문·회의록), 위키 원본 [wiki-raw/](wiki-raw/)
- 전사기: [transcribe.py](transcribe.py)(faster-whisper base, CPU, int8), 의존성 [requirements-whisper.txt](requirements-whisper.txt)
- 음원 제작기(저자용): [make_audio.py](make_audio.py)
- 9장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)

> 확인 범위: 1분 합성 음원의 Whisper 전사(저자 Linux 장비), 상용 API 추출, 게시 묶음·위키 정리를 2026-10-15에 실행했습니다. 5분 본실습 음원·사람 녹음·두 기준 장비의 전사 시간은 확인 전입니다.

## 9.1 준비

```bash
python3 part3.py prepare --workspace work-meeting --wiki-from ch08
```

회의 정보는 [start/meeting.json](start/meeting.json)(MEET-BB-1008, 출처 사건 EV-BB-1008-CALL)입니다.

## 9.2 로컬 전사

```bash
uv run --no-project --python 3.11 --with-requirements ch09/requirements-whisper.txt \
  python ch09/transcribe.py --workspace work-meeting
```

첫 실행에는 모델 내려받기가 있습니다. 결과 `output/transcript.json`에는 구간별 시작·끝 시각, 로딩·전사 시간, measured-transcription 표시가 남습니다. 전사를 건너뛰려면 저자 대본을 전사문 형식으로 넣습니다(새 폴더에서).

```bash
python3 part3.py transcript-reference --workspace work-meeting   # audio_transcribed false
```

## 9.3 결정 사항과 할 일 추출

```bash
python3 part3.py extract --workspace work-meeting --engine api       # 상용 API 직접
python3 part3.py extract --workspace work-meeting                    # 헤르메스(--query-file)
python3 part3.py extract --workspace work-meeting --reference        # 비교용 회의록
```

자동 검사(`validate_minutes`): 회의 ID·출처 사건 일치, decisions·cancelled·actions·unknown 목록, 결정마다 상태(confirmed·tentative·cancelled)·근거·ID·내용, 정수 판. 사실 대조는 사람이 합니다. 기대 결과: 발행일 10/15 확정, 10/12 검수 담당자 확인은 잠정, 금요일 다음 회의안 취소, PM 할 일의 기한은 미정.

## 9.4 회의록 게시와 위키 반영

```bash
python3 part3.py publish --workspace work-meeting           # 게시 대기 묶음
python3 part3.py confirm --workspace work-meeting --by PM   # 사람이 확인한 뒤 status를 confirmed로
python3 part3.py wiki ch09-meeting-record --workspace work-meeting --engine api
```

`publish`가 `output/wiki-input/`에 만드는 것:

- `20261008_BB_CAMP-BB-202610_meeting.md`: 머리말(회의 ID·고객·캠페인·날짜·출처 사건·판·status publication_pending·녹음 해시·녹음 위치는 위키 밖·전체 전사문 해시) + 결정·취소·할 일·미정 조건 네 목록
- `20261008_BB_CAMP-BB-202610_transcript.md`: `[00:12~00:18] 문장` 형식의 전사문 삭제판. 주소·전화번호는 자동으로 `[삭제: 개인정보]`로 바꾸고, 참석자 이름은 `input/redact.txt`에 한 줄씩 적어 지웁니다. 업무 밖 발언은 사람이 지웁니다. 결정의 근거 문장이 삭제판에 남았는지 `evidence_missing_after_redaction`으로 알려 줍니다.
- 전사 JSON·회의록 JSON(위키에 넣지 않음)

위키 정리는 두 원본을 넣고 확정 결정은 `wiki/decisions/20261008_BB-publish-plan.md`에, 잠정·취소는 상태를 그대로 남깁니다. 자동 검사: 결정 페이지에 2026-10-15·tentative·cancelled·회의록 원본 출처, 캠페인 페이지에 회의록 출처. 사람이 볼 것: 잠정 결정을 확정처럼 옮기지 않았는지, 취소된 회의가 할 일로 남지 않았는지.

## 되돌아갈 자리

- 원본 음원·대본·용어표: [start/](start/)
- 코드: [../part3.py](../part3.py)의 `extract_minutes`·`validate_minutes`·`publish_bundle`·`redact`·`confirm_bundle`, [transcribe.py](transcribe.py)
