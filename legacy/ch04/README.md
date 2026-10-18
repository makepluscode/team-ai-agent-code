# 4장 콘텐츠 업무 자동화

『팀 AI 에이전트 실전』 4장의 실습 안내입니다. 봉봉소프트 제품 소개 캠페인(CAMP-BB-202610) 하나로 자료 조사, SNS 게시물, 뉴스레터, 주간 보고 네 가지 업무를 하고, 장 끝에 결과를 팀 위키에 정리합니다.

- 원고: `content/ch04_content-work_v0.md`(도서 저장소)
- 이 폴더: 시작 자료 [start/](start/), 지시문 [prompts/](prompts/), 실습 정의 [tasks.json](tasks.json), 비교용 결과 [completed/](completed/)
- 4장 끝 상태의 비교용 위키: [completed/studio-merry-wiki/](completed/studio-merry-wiki/)
- 실행기: 저장소 맨 위의 [../run.py](../run.py)(2~6장 공통), 위키 정리 [../wiki.py](../wiki.py)

> 확인 범위: 제공 코드의 계산·검사와 상용 API 직접 호출 경로(`--engine api`, 제미나이 2.5 Flash)는 2026-10-15에 실행했습니다. 헤르메스 경로와 두 기준 장비, 실제 웹 도구는 확인 전입니다. 비교용 결과는 저자가 작성한 예시이며 모델 응답이 아닙니다.

## 시작 전에

2·3장의 작업 폴더를 그대로 씁니다. 없으면 새로 만듭니다. `prepare`는 모든 장의 시작 자료를 `work/input`에 모으고 연습 위키 `work/wiki`를 만듭니다. 자기 팀 위키(`~/studio-merry-wiki`)를 쓰려면 `--wiki`로 지정합니다.

```bash
cd ~/team-ai-agent-code
python3 run.py prepare --workspace work                                  # 연습 위키(2장 시작 상태)
python3 run.py prepare --workspace work --wiki-from ch03                 # 3장 끝 위키로 시작(앞 장을 건너뛸 때)
python3 run.py prepare --workspace work --wiki ~/studio-merry-wiki       # 내 팀 위키를 읽게 함
```

모델 실습은 세 경로 중 하나로 합니다. 결과 파일과 확인 기준은 같습니다.

| 경로 | 명령 | 비고 |
|---|---|---|
| 지시문 붙여 넣기 | `python3 run.py prompt <ID> --workspace work`로 출력해 `hermes chat`에 붙여 넣음 | 원고의 '만들어 보기' |
| 제공 코드 + 헤르메스 | `python3 run.py run <ID> --workspace work` | `hermes chat --oneshot --query-file`로 지시문 전달 |
| 제공 코드 + 상용 API | `python3 run.py run <ID> --workspace work --engine api` | 헤르메스 없이 지시문과 읽을 파일을 API에 보냄. 키는 환경 변수(`ANTHROPIC_API_KEY`·`OPENAI_API_KEY`·`GEMINI_API_KEY`) |

결과 형식만 보려면 새 작업 폴더에서 `--reference`를 붙입니다. 비교용 결과를 복사할 뿐이며 모델 실행으로 세지 않습니다.

## 4.1 자료 조사

| 항목 | 내용 |
|---|---|
| 실습 ID | `ch04-research` |
| 지시문 | [prompts/ch04-research.txt](prompts/ch04-research.txt) |
| 읽는 것 | 위키 `wiki/clients/BB.md`·`wiki/campaigns/CAMP-BB-202610.md`·`wiki/research/content-review.md`·`guides/brands/BB.md`, 시작 자료 `product.md`·`reports.md` |
| 결과 | `work/output/research.md` |
| 자동 확인 | '봉봉소프트'·'REPORT'·'확인 필요'가 있음, 입력이 바뀌지 않음 |

```bash
python3 run.py run ch04-research --workspace work --engine api
```

사람이 확인할 것: 근거 칸의 자료 ID가 그 문단의 내용과 맞는지, 위키에 이미 있는 내용을 다시 조사하지 않았는지, 시장 규모·효과를 만들지 않았는지. 비교용: [completed/research.md](completed/research.md)

## 4.2 SNS 게시물 초안

| 항목 | 내용 |
|---|---|
| 실습 ID | `ch04-sns` |
| 지시문 | [prompts/ch04-sns.txt](prompts/ch04-sns.txt) |
| 읽는 것 | 위키 `guides/brands/BB.md`·캠페인 페이지, `product.md`·`previous-posts.json`(20건)·`content-brief.md`·`events.json` |
| 결과 | `work/output/sns-draft.md` |
| 자동 확인 | 필수 '봉봉소프트'·'확인 필요'. **금지**: 초안 부분에 단종 기능 '자동 견적 발송'(POST-BB-020의 함정) |

```bash
python3 run.py run ch04-sns --workspace work --engine api
python3 run.py check ch04-sns --workspace work
```

금지 낱말 검사는 '사용한 사실'·'쓰지 않은 것'·'확인 필요' 같은 제목 앞의 초안 부분만 봅니다. 모델이 단종 기능을 '쓰지 않은 것'으로 밝힌 것은 실패가 아닙니다. 비교용: [completed/sns-draft.md](completed/sns-draft.md)

## 4.3 뉴스레터 초안

| 항목 | 내용 |
|---|---|
| 실습 ID | `ch04-newsletter` |
| 지시문 | [prompts/ch04-newsletter.txt](prompts/ch04-newsletter.txt) |
| 결과 | `work/output/newsletter-draft.md` |
| 자동 확인 | '프리헤더'·'CTA'·'확인 필요'. 금지: 초안 부분의 '50%'(입력에 없는 효과) |

발송 전 확인 4항목(링크·수신 대상·발신 이름·검수자 승인)이 표로 남는지 봅니다. 비교용: [completed/newsletter-draft.md](completed/newsletter-draft.md)

## 4.4 캠페인 주간 보고

모델 없이 제공 코드가 계산합니다(`run.py`의 `performance`).

```bash
python3 run.py run ch04-weekly-report --workspace work
```

기대값: SNS(10/05~10/08) CTR 2.00%, 뉴스레터 3.00%, 9/28~10/01 SNS는 클릭이 비어 '확인 필요'. 결측값을 0으로 채우지 않고 기간이 다른 행의 증감을 계산하지 않습니다. 비교용: [completed/weekly-report.md](completed/weekly-report.md)

## 위키에 넣기 — `ch04-wiki-ingest`

네 결과를 원본 이름([표 4.1])으로 위키 `raw/`에 넣고 3.4의 정리 지시문으로 정리합니다. 자기 결과 파일이 있으면 그 파일에 머리말(client·campaign·date·kind·made_by·made_from)을 붙여 넣고, 없으면 이 폴더의 비교용 결과를 넣습니다.

| 원본 | 정리되는 페이지 |
|---|---|
| raw/20261006_BB_CAMP-BB-202610_research.md | wiki/research/(새 페이지), 캠페인 페이지의 검토할 질문 |
| raw/20261007_BB_CAMP-BB-202610_sns-draft.md | 캠페인 페이지의 산출물 |
| raw/20261007_BB_CAMP-BB-202610_newsletter-draft.md | 캠페인 페이지의 산출물 |
| raw/20261008_BB_CAMP-BB-202610_weekly-report.md | 캠페인 페이지의 성과 기록 |

```bash
python3 run.py prompt ch04-wiki-ingest --workspace work            # 원본별 지시문 네 개
python3 run.py run ch04-wiki-ingest --workspace work --engine api  # 원본 1건당 1회 호출
```

자동 검사: 원본 불변, `log.md` 덧붙이기만, 캠페인 페이지에 네 원본의 이름과 '확인 필요', 리서치 페이지가 index.md에 연결. 결과 기록은 `work/output/wiki-runs/ch04-wiki-ingest.json`입니다. 가설 문장이 '확인된 성과'로 옮겨졌는지는 사람이 봅니다.

비교용 위키와 대조: `diff -r work/wiki/wiki ch04/completed/studio-merry-wiki/wiki`

## 되돌아갈 자리

- 시작 자료: [start/](start/), 지시문: [prompts/](prompts/)
- 실패한 실습은 새 작업 폴더에서: `python3 run.py prepare --workspace work-retry --wiki-from ch03`
- 계산 코드: [../run.py](../run.py)의 `performance`, 검사: `verify`·`draft_part`
