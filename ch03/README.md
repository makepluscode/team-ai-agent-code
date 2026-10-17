# 3장 팀 위키에 기준 쌓기

『팀 AI 에이전트 실전』 3장의 실습 안내입니다. 이 문서만 보고 따라 할 수 있게 썼습니다. 2장을 마쳐 홈 폴더에 `team-ai-agent-code`(예제 저장소)와 `studio-merry-wiki`(팀 위키)가 있다고 봅니다.

- 원고: `content/ch03_basic-recipes_v0.md`(도서 저장소)
- 결과물: 기초 레시피 열두 개(스킬 3개, 예약 2개 포함), 위키 동기화 스킬, 정리되기 시작한 팀 위키
- 이 폴더의 자료
  - [completed/studio-merry-wiki/](completed/studio-merry-wiki/) — 3.4까지 정리한 위키의 비교용 결과
  - [completed/teammate-questions.md](completed/teammate-questions.md) — 3.5 동료 실습의 비교용 결과
- 이 장의 시작 자료 [start/](start/), 지시문 원본 [prompts/](prompts/), 실습 정의 [tasks.json](tasks.json), 비교용 결과 [completed/](completed/). 실행기는 저장소 맨 위의 [../run.py](../run.py)

> 확인 범위: 제공 코드의 로컬 처리(파일 정리·이름 변경·검사)와 위키 동기화 실행 파일은 시험했습니다. 헤르메스의 모델 응답, 스킬 tap 설치, 예약 실행은 기준 장비에서 아직 확인하지 않았습니다. 비교용 결과는 저자가 작성한 예시이며 모델 응답이 아닙니다.

## 시작 전에

모든 명령은 **Ubuntu** 에서 실행합니다. 2장에서 만든 작업 폴더를 그대로 쓰고, 없으면 새로 만듭니다.

```bash
cd ~/team-ai-agent-code
ls work 2>/dev/null || python3 run.py prepare --workspace work
```

이 장의 실습은 팀원 모두가 똑같이 하지 않습니다. 지침·위키·스킬·예약은 **담당자** 한 명이 만들고, **다른 팀원**은 받아서 씁니다. 혼자 연습한다면 담당자 역할로 진행하고, 동료 역할은 2장 4-4처럼 위키를 다른 이름(`~/studio-merry-wiki-2`)으로 한 번 더 받아서 연습합니다.

| 절 | 담당자(스튜디오 메리는 PM) | 다른 팀원 |
|---|---|---|
| 3.1 | 공통·고객별 지침을 정리해 위키에 저장 | 받은 SOUL.md를 자기 헤르메스에 적용 |
| 3.2~3.3 | 레시피 실행 | 레시피 실행(각자의 작업 폴더) |
| 3.4 | 원본을 위키 페이지로 정리 | 정리할 원본을 raw 폴더에 넣기 |
| 3.5 | 동기화 스킬 설치, 정리한 페이지 올리기 | 동기화 스킬 설치, 받은 페이지로 일하기 |
| 3.6 | 스킬을 만들어 위키에 올리기 | tap으로 스킬 설치와 갱신 |
| 3.7 | 예약 등록과 결과 확인 | 동기화로 결과 받아 보기 |

모든 레시피는 같은 순서입니다. **결과를 만들고 → 확인 기준으로 대조하고 → 한 가지를 고칩니다.** 실패하면 `--workspace work-retry`로 새 작업 폴더를 만들어 같은 실습 ID로 다시 합니다.

---

## 3.1 팀의 맥락 알려주기

레시피 두 개: **대행사 공통 말투**, **고객사별 브랜드 지침**. 원본은 위키의 `guides/`에 두고, 공통 말투(SOUL.md)는 각자 헤르메스에 적용합니다.

입력: `work/input/common-style.md`, `work/input/brands/BB.md·DP.md·LB.md`

### 만들어 보기 (담당자)

`hermes chat`에 붙여 넣습니다.

```text
스튜디오 메리의 공통 응답 지침을 정리해 줘.

입력은 ~/team-ai-agent-code/work/input/common-style.md 야.
대행사 전체에 적용할 말투, 피할 표현, 불확실한 내용을 표시하는 방식을 나눠 줘.
고객사 하나에만 해당하는 제품명·성과·캠페인 조건은 공통 지침에서 분리해 줘.
공통 지침 초안을 먼저 보여 주고, 내가 확인한 뒤 ~/studio-merry-wiki/guides/SOUL.md 에 저장해 줘.
기존 파일은 확인 없이 덮어쓰지 마.

이어서 ~/team-ai-agent-code/work/input/brands 폴더를 읽고
봉봉소프트·데얼즈파이·런던뷰티랩의 지침을 ~/studio-merry-wiki/guides/brands 에
BB.md, DP.md, LB.md 별도 파일로 정리해 줘.
입력에 없는 브랜드 특징은 새로 만들지 마.
```

### 제공 코드로 진행하기 (담당자)

```bash
python3 run.py run ch03-common-style --workspace work
python3 run.py run ch03-client-guides --workspace work
```

결과(`work/output/SOUL.md`, `work/output/client-guides.md`)를 확인한 뒤 위키로 옮깁니다. 고객별 파일은 시작 자료의 세 파일을 씁니다.

```bash
cp work/output/SOUL.md ~/studio-merry-wiki/guides/SOUL.md
cp work/input/brands/*.md ~/studio-merry-wiki/guides/brands/
```

### 공통 말투 적용 (모두)

SOUL.md는 헤르메스 설정 폴더(HERMES_HOME, WSL2와 맥은 `~/.hermes`)에 있어야 읽힙니다. 기존 파일을 보관한 뒤 적용합니다. 3.5절의 동기화 스킬을 설치한 뒤에는 `soul-check`·`soul-apply`가 이 일을 대신합니다.

```bash
[ -f ~/.hermes/SOUL.md ] && cp ~/.hermes/SOUL.md ~/.hermes/SOUL.md.bak-$(date +%Y%m%d)
cp ~/studio-merry-wiki/guides/SOUL.md ~/.hermes/SOUL.md
```

### 확인

같은 질문을 적용 전후로 해 봅니다: `봉봉소프트를 한 문장으로 소개해 줘`. 그다음 고객만 바꿔 봅니다.

```text
~/studio-merry-wiki/guides/brands/BB.md 지침으로 ~/team-ai-agent-code/work/input/product.md 를 두 문장으로 소개해 줘.
```

```text
~/studio-merry-wiki/guides/brands/DP.md 지침으로 같은 일을 해 줘. 데얼즈파이의 제품 자료가 없으면 '확인 필요'로 남겨 줘.
```

- [ ] 적용 후 응답에 근거 없는 성과 수치가 없음
- [ ] 공통 지침에 특정 고객의 제품명·조건이 없음
- [ ] 고객별 결과에 다른 고객의 표현이 섞이지 않음

비교용 결과: [completed/SOUL.md](completed/SOUL.md), [completed/client-guides.md](completed/client-guides.md)

**개선 한 번**: 홍보 문구처럼 들리는 문장 하나를 골라, 그 표현이 왜 맞지 않는지와 대신 쓸 방향을 지침에 한 줄 더하고 다시 실행합니다.

**되돌아갈 자리**: `cp ~/.hermes/SOUL.md.bak-<날짜> ~/.hermes/SOUL.md`로 이전 말투를 되살립니다.

---

## 3.2 파일 정리와 이름 규칙

레시피 두 개: **캠페인별 소재 정리**, **파일명 규칙 일괄 적용**. 원본은 그대로 두고 작업용 복사본에만 적용합니다. 이 두 실습은 모델 없이 제공 코드만으로 끝납니다.

입력: `work/input/assets/`(소재 3개와 manifest.json)

### 만들어 보기

```text
~/team-ai-agent-code/work/input/assets 에 있는 파일을 캠페인별로 정리해 줘.

먼저 파일 목록과 manifest.json을 읽고 고객·캠페인을 확인할 수 있는 근거를 적어 줘.
분류가 모호하면 '확인 필요'로 남겨 줘.
파일을 바로 옮기지 말고 원래 위치와 제안 위치의 대응표를 만들어 줘.

내가 정리안을 확인한 뒤 ~/team-ai-agent-code/work/output/organized 에 복사본으로 적용해 줘.
원본은 보존하고 같은 이름의 파일을 덮어쓰지 마.
작업이 끝나면 입력 파일 수와 복사한 파일 수, 확인 필요 파일 수를 대조해 줘.

이어서 복사본의 이름을 YYYYMMDD_고객ID_캠페인ID_종류 규칙으로 바꾸는 대응표를 만들어 줘.
서로 다른 두 파일이 같은 새 이름이 되면 바꾸지 말고 충돌 목록으로 보여 줘.
```

### 제공 코드로 진행하기

```bash
python3 run.py run ch03-organize --workspace work
python3 run.py run ch03-rename --workspace work
cat work/output/asset-map.json work/output/rename-map.json
```

### 확인

- [ ] 입력 3개 = 정리 2개 + 확인 필요 1개('고객 미상.txt')
- [ ] `work/input/assets`의 원본이 그대로 있음
- [ ] 새 이름이 규칙을 따르고 충돌이 없음

비교용 결과: [completed/asset-map.json](completed/asset-map.json), [completed/rename-map.json](completed/rename-map.json)

**개선 한 번**: 확정한 파일명 규칙이 위키의 규칙 파일(`~/studio-merry-wiki/AGENTS.md`의 '원본' 항목)과 같은지 확인합니다. 위키에 원본을 넣을 때도 같은 규칙을 씁니다.

**되돌아갈 자리**: 새 작업 폴더(`work-retry`)에서 다시 실행합니다.

---

## 3.3 자료 요약과 웹 수집

레시피 두 개: **업계 리포트 한 장 요약**, **경쟁사 콘텐츠 모니터링과 비교표**.

입력: `work/input/reports.md`, `work/input/competitors.md`, `work/input/web-snapshots.md`(웹을 미리 저장해 둔 합성 자료)

### 만들어 보기 — 리포트 요약

```text
~/team-ai-agent-code/work/input/reports.md 를 읽고 캠페인 준비용 요약을 만들어 줘.

구성은 핵심 관찰, 확인된 수치와 조사 조건, 적용할 때의 한계,
봉봉소프트 기획에서 검토할 질문으로 나눠 줘.
자료의 사실과 네가 제안한 해석은 구분해 줘.
핵심 주장에는 자료 ID(REPORT-01 등)를 적어 줘.
읽지 못한 부분은 읽지 못했다고 표시해 줘.
결과는 ~/team-ai-agent-code/work/output/report-summary.md 에 저장해 줘.
```

### 만들어 보기 — 모니터링과 비교표

```text
~/team-ai-agent-code/work/input/web-snapshots.md 와 competitors.md 를 읽고
키워드 '작업 상태', '문의 접수'와 관련된 경쟁사 콘텐츠 목록을 만들어 줘.
이 자료는 웹을 미리 저장해 둔 연습용이므로 .example 주소에 접속하지 마.

각 항목에 제목 또는 메시지, 원문 주소, 보관일을 남겨 줘.
수집에 실패한 항목은 '확인 필요'로 따로 남겨 줘.
이번 자료를 최초 기준으로 저장하고, 새로 바뀐 항목이라고 단정하지 마.

이어서 경쟁사 메시지 비교표를 만들어 줘.
열은 대상 고객, 먼저 꺼내는 문제, 핵심 메시지, 근거, 확인 불가로 하고
자료에 없는 가격이나 성과는 채우지 마.
목록은 ~/team-ai-agent-code/work/output/monitoring.md,
비교표는 ~/team-ai-agent-code/work/output/comparison.md 에 저장해 줘.
```

실제 웹에서 해 보고 싶다면 공개된 경쟁사 페이지 주소 두세 개로 바꿔 같은 지시문을 씁니다. 헤르메스의 웹 도구가 설정돼 있어야 하며, 직접 열지 못한 페이지는 결과에 따로 남는지 확인합니다.

### 제공 코드로 진행하기

```bash
python3 run.py run ch03-report-summary --workspace work
python3 run.py run ch03-monitoring --workspace work
python3 run.py run ch03-comparison --workspace work
```

### 확인

- [ ] 요약의 주장마다 REPORT-01·02가 붙어 있고, 두 자료가 '설명용 시나리오'라는 한계가 남아 있음
- [ ] 효과의 크기처럼 자료에 없는 수치를 만들지 않음
- [ ] 모니터링에 WEB-03이 '수집 실패·확인 필요'로 남아 있음
- [ ] 비교표에 가격·절감 시간을 채우지 않음

비교용 결과: [report-summary.md](completed/report-summary.md), [monitoring.md](completed/monitoring.md), [comparison.md](completed/comparison.md)

**개선 한 번**: 비교표에 '먼저 꺼내는 문제' 열이 없다면 더하고, 늘어난 칸이 원문과 맞는지 확인합니다.

---

## 3.4 위키에 정리하기

레시피 하나: **원본 한 건을 위키 페이지로 정리**. LLM 위키의 '수집'을 가장 작은 단위로 해 봅니다. 위키 페이지 정리는 **담당자 한 명**이 합니다.

첫 원본은 2장에서 읽은 `raw/20261005_BB_brief.md`입니다. 이미 위키에 들어 있습니다.

### 만들어 보기 (담당자)

위키 폴더에서 헤르메스를 실행합니다. 헤르메스는 실행 폴더의 `AGENTS.md`(규칙 파일)를 자동으로 읽습니다.

```bash
cd ~/studio-merry-wiki
hermes chat
```

```text
팀 위키에 원본 하나를 정리해 줘.

먼저 AGENTS.md(규칙 파일)와 wiki/index.md를 읽고 정리 규칙을 요약해 줘.

정리할 원본은 raw/20261005_BB_brief.md 야. 원본은 고치지 마.
규칙 파일에 따라 관련 위키 페이지를 새로 만들거나 고쳐 줘.
페이지의 각 내용에는 출처 원본 파일을 적어 줘.
원본에 없는 사실은 쓰지 말고, 미정인 조건은 '확인 필요'로 남겨 줘.
기존 페이지와 다른 내용이 있으면 덮어쓰지 말고 서로 다르다고 표시해 줘.

index.md에 페이지를 추가하고 log.md에 오늘 날짜로 정리 기록을 한 줄 남겨 줘.
끝나면 바뀐 파일 목록과 파일별 변경 내용을 보여 줘. 저장소에 올리지는 마.
```

### 확인

```bash
git -C ~/studio-merry-wiki status --short
git -C ~/studio-merry-wiki diff --stat
```

- [ ] `raw/` 아래 파일은 목록에 없음(원본을 고치지 않음)
- [ ] `wiki/clients/BB.md`(와 캠페인 페이지)가 새로 생기고, 사실 문장마다 `(출처: raw/...)`가 붙음
- [ ] 채널·분량·검수 담당자·발행일이 '확인 필요'로 남음
- [ ] `wiki/index.md`와 `wiki/log.md`가 함께 바뀜

비교용 결과: [completed/studio-merry-wiki/wiki/](completed/studio-merry-wiki/wiki/)

### 개선 한 번 — 두 번째 원본

3.3의 리포트 요약을 규칙에 맞는 이름으로 위키 원본에 넣고 같은 지시문을 다시 실행합니다. 지시문의 원본 경로만 바꿉니다.

```bash
cp ~/team-ai-agent-code/work/output/report-summary.md ~/studio-merry-wiki/raw/20261006_TEAM_report-summary.md
```

- [ ] `wiki/research/` 아래에 새 페이지가 생기고 index.md에 '리서치' 줄이 더해짐
- [ ] 기존 봉봉소프트 페이지를 지우고 새로 쓰지 않음

### 제공 코드로 진행하기

모델 없이 결과 형식만 보거나, 결과가 크게 다를 때 대조합니다.

```bash
diff -r ~/studio-merry-wiki/wiki ~/team-ai-agent-code/ch03/completed/studio-merry-wiki/wiki
```

문장이 달라도 확인 항목 네 가지가 맞으면 통과입니다.

제공 코드는 작업 폴더 안의 연습 위키(`work/wiki`)에서 같은 정리를 하고 검사까지 합니다. 헤르메스가 위키 폴더에서 정리하고, 헤르메스가 없으면 `--engine api`로 같은 지시문을 상용 API에 보내 응답의 페이지만 `wiki/` 아래에 씁니다. 3.3의 리포트 요약(`work/output/report-summary.md`)이 있으면 그 파일을 두 번째 원본으로 넣습니다.

```bash
python3 run.py run ch03-wiki-ingest --workspace work               # 헤르메스
python3 run.py run ch03-wiki-ingest --workspace work --engine api  # 상용 API 직접
python3 run.py prompt ch03-wiki-ingest --workspace work            # 붙여 넣을 지시문 보기
```

검사 항목: 원본(`raw/`)이 바뀌지 않음, 고객 페이지와 리서치 페이지에 출처 표기, `index.md`에 페이지 연결, `log.md`는 덧붙이기만 함. 원본 메모에 캠페인 ID가 없으므로 캠페인 페이지는 만들지 않아도 통과입니다(2026-10-15 제미나이 실행에서 모델이 캠페인 페이지를 만들지 않은 것이 규칙에 맞는 동작이었습니다). 결과 기록은 `work/output/wiki-runs/ch03-wiki-ingest.json`입니다.

**되돌아갈 자리**: 아직 올리지 않았으므로 바뀐 페이지를 버리고 다시 실행할 수 있습니다. 새로 생긴 파일만 지우고 목록·기록은 되돌립니다.

```bash
cd ~/studio-merry-wiki
git restore wiki/index.md wiki/log.md
git clean -n wiki/          # 지울 파일 목록을 먼저 확인
git clean -f wiki/          # 확인한 뒤 지움
```

---

## 3.5 위키 동기화

정리한 페이지를 올리고, 다른 팀원이 받아서 그 페이지로 일하게 합니다. Git 명령 대신 저자가 제공하는 **위키 동기화 스킬**([../ch02/wiki-starter/skills/wiki-sync/SKILL.md](../ch02/wiki-starter/skills/wiki-sync/SKILL.md))을 씁니다. 레시피 수에는 세지 않습니다.

### 스킬 설치 (모두, 처음 한 번)

팀 위키는 비공개 저장소이므로 헤르메스가 스킬을 받으려면 GitHub 접근 정보가 따로 필요합니다. 2장의 gh 로그인은 Git으로 받고 올리는 연결이고, 헤르메스의 스킬 받기(tap)와는 별개입니다.

1. GitHub에서 토큰을 만듭니다: Settings → Developer settings → Personal access tokens → Fine-grained tokens. 저장소는 `studio-merry-wiki`만, 권한은 Contents 읽기(Read-only)만 줍니다.
2. 자기 헤르메스 설정 파일 `~/.hermes/.env`에 한 줄 추가합니다. 이 파일은 위키에 올리지 않습니다.

   ```bash
   nano ~/.hermes/.env      # GITHUB_TOKEN=<만든 토큰> 한 줄을 넣고 저장
   ```

3. 팀 위키를 스킬 출처로 등록하고 동기화 스킬을 설치합니다.

   ```bash
   hermes skills tap add <팀 계정>/studio-merry-wiki
   hermes skills install <팀 계정>/studio-merry-wiki/skills/wiki-sync
   hermes skills tap list
   ```

처음 설치할 때 외부 스킬이라는 경고와 보안 검사가 나올 수 있습니다. 팀 저장소의 스킬이 맞는지 확인하고 진행합니다.

> TODO(검증): 토큰 대신 gh 로그인 정보를 쓸 수 있는지, 처음 설치 화면의 문구.

### 만들어 보기 — 올리기 (담당자)

위키 폴더에서 헤르메스를 열고 요청합니다.

```bash
cd ~/studio-merry-wiki
hermes chat
```

```text
위키 동기화해 줘.
```

스킬이 다음 순서로 진행합니다. 순서마다 화면을 확인합니다.

1. 바뀐 파일 목록을 보여 줍니다. **올릴 파일을 고릅니다.** 3.4의 페이지와 index.md, log.md, (개선 단계를 했다면) 새 원본만 고릅니다. 실습 결과나 키 파일이 보이면 고르지 않습니다.
2. 기록 문구를 제안합니다(예: `[PM] 봉봉소프트 고객·캠페인 페이지 정리 · 첫 메모 수집`). 고치거나 승인합니다.
3. 다른 팀원의 변경을 받아 와 합칩니다.
4. 저장소에 올립니다.
5. 위키의 SOUL.md가 지금 적용한 것과 다르면 알려 줍니다. 적용할지 정합니다.

### 만들어 보기 — 받아서 일하기 (다른 팀원)

```bash
cd ~/studio-merry-wiki
hermes chat
```

```text
위키 동기화해 줘.
```

받은 페이지를 열어 보는 데서 끝내지 않고, 그 페이지로 일을 하나 시킵니다.

```text
~/studio-merry-wiki/wiki/clients/BB.md 를 읽고,
봉봉소프트에 첫 통화 전에 확인할 질문을 우선순위 순으로 정리해 줘.
페이지에 '확인 필요'로 남은 조건은 모두 질문에 넣고,
페이지에 없는 사실은 쓰지 마.
질문마다 근거가 된 페이지의 줄과 원본 파일을 적어 줘.
```

- [ ] 질문에 채널·분량·검수 담당자·발행일 네 가지가 모두 들어감
- [ ] 질문마다 `wiki/clients/BB.md`와 `raw/20261005_BB_brief.md`로 이어지는 근거가 붙음
- [ ] 동료는 원본 메모를 직접 받은 적이 없는데도 같은 기준의 결과가 나옴

비교용 결과: [completed/teammate-questions.md](completed/teammate-questions.md)

### 개선 한 번 — 충돌 만들어 보기

두 사람이 `guides/brands/BB.md`의 같은 줄을 서로 다르게 고친 뒤 차례로 '위키 동기화해 줘'를 요청합니다.

- [ ] 먼저 올린 사람은 성공함
- [ ] 나중 사람의 스킬은 받아 오기에서 멈추고 두 판을 보여 줌
- [ ] 남길 판을 사람이 정해 알려 주면, 그 파일만 기록하고 다시 올림
- [ ] 두 사람의 기록이 모두 이력에 남음(`git -C ~/studio-merry-wiki log --format="%an %s" -5`)

취소하고 싶으면 `받아 오기를 취소해 줘`라고 요청합니다.

### 제공 코드로 진행하기

스킬이 실행하는 파일을 직접 실행해도 같은 결과가 나옵니다. 위키 폴더에서 실행합니다.

```bash
cd ~/studio-merry-wiki
S=skills/wiki-sync/scripts/wiki_sync.py
python3 $S status
python3 $S commit -m "[PM] 봉봉소프트 페이지 정리" wiki/clients/BB.md wiki/campaigns/CAMP-BB-202610.md wiki/index.md wiki/log.md
python3 $S pull
python3 $S push
python3 $S soul-check
```

다른 팀원은 `python3 $S pull`만 해도 받습니다. 명령이 종료 코드 2로 멈추면 출력된 안내를 따릅니다. 멈춘 상태를 풀려고 다른 Git 명령을 쓰지 않습니다.

**되돌아갈 자리**: 잘못 올린 변경은 `어제 올린 봉봉소프트 페이지 변경을 되돌려 줘`라고 요청합니다. 직접 할 때는 `python3 $S history wiki/clients/BB.md`로 기록 ID를 찾고 `python3 $S revert <기록 ID>` 다음 `python3 $S push`를 실행합니다. 되돌린 사실도 새 기록으로 남습니다.

---

## 3.6 스킬 저장과 팀 배포

레시피 세 개: **콘텐츠 초안 스킬**, **브랜드 용어 교정 스킬**, **주간 성과 정리 스킬**. 담당자가 만들어 위키에 올리고, 팀원은 tap으로 설치합니다.

### 만들어 보기 (담당자) — 콘텐츠 초안 스킬

```text
지금까지 확인한 콘텐츠 초안 작성 절차를 헤르메스 스킬 초안으로 정리해 줘.

이름은 content-draft로 두고,
고객사, 위키의 고객 페이지와 고객별 브랜드 지침, 제품 소개, 게시할 채널을 입력으로 받게 해 줘.
빠진 입력은 먼저 묻거나 '확인 필요'로 남겨 줘.

절차에는 자료 읽기, 초안 작성, 입력과의 사실 대조,
고객 혼동·금지 표현 확인, 별도 결과 파일 저장을 넣어 줘.
외부 발행은 포함하지 마.
스킬 내용과 사용 예시를 먼저 보여 줘.
내가 확인하면 ~/studio-merry-wiki/skills/content-draft/SKILL.md 에 저장해 줘.
```

같은 방식으로 두 스킬을 더 만듭니다.

- `brand-edit`: 고객 지침과 초안을 읽어 원문·수정안·이유를 표로. 제품 사실은 바꾸지 않고 의심되면 '확인 필요'.
- `weekly-report`: 성과 CSV의 기간과 지표를 확인하고, 계산과 해석을 나눔. 기간이 다른 행은 비교하지 않고, 빈 값은 0이 아니라 '미확인'.

### 제공 코드로 진행하기 (담당자)

```bash
cd ~/team-ai-agent-code
python3 run.py run ch03-content-skill --workspace work
python3 run.py run ch03-brand-skill --workspace work
python3 run.py run ch03-weekly-skill --workspace work
cp -r work/output/skills/* ~/studio-merry-wiki/skills/
```

### 배포

담당자가 위키에 올립니다.

```bash
cd ~/studio-merry-wiki && hermes chat
```

```text
위키 동기화해 줘. 이번에는 skills 폴더의 새 스킬 세 개만 올려 줘.
```

다른 팀원이 설치합니다. tap은 3.5에서 이미 등록했습니다.

```bash
hermes skills install <팀 계정>/studio-merry-wiki/skills/content-draft
hermes skills install <팀 계정>/studio-merry-wiki/skills/brand-edit
hermes skills install <팀 계정>/studio-merry-wiki/skills/weekly-report
```

### 확인

동료가 자기 헤르메스에서 두 고객으로 같은 스킬을 써 봅니다.

```text
content-draft 스킬로 봉봉소프트 SNS 게시물 초안을 만들어 줘.
고객 페이지 ~/studio-merry-wiki/wiki/clients/BB.md, 지침 ~/studio-merry-wiki/guides/brands/BB.md,
제품 소개 ~/team-ai-agent-code/work/input/product.md 를 써 줘.
결과는 ~/team-ai-agent-code/work/output/bb-sns-draft.md 에 저장해 줘.
```

```text
content-draft 스킬로 데얼즈파이 뉴스레터 초안을 만들어 줘.
지침은 ~/studio-merry-wiki/guides/brands/DP.md 이고, 제품 자료가 없으면 '확인 필요'로 남겨 줘.
결과는 ~/team-ai-agent-code/work/output/dp-newsletter-draft.md 에 저장해 줘.
```

- [ ] 두 결과 모두 '사용한 사실'과 '확인할 조건'이 나뉨
- [ ] 봉봉소프트 초안에 위키 페이지의 미정 조건이 '확인 필요'로 반영됨
- [ ] 두 결과에 다른 고객의 표현이 섞이지 않음
- [ ] `weekly-report`로 `work/input/performance.csv`를 정리하면 SNS CTR 2.00%, newsletter CTR 3.00%, 9/28~10/01 행은 비교에서 제외

비교용 결과: [completed/skills/](completed/skills/)

### 스킬 갱신

담당자가 위키의 스킬을 고쳐 다시 올리면, 팀원은 확인하고 받습니다.

```bash
hermes skills check
hermes skills update
```

자기 컴퓨터에서 설치한 스킬을 직접 고치면 `update`가 그 스킬을 건너뜁니다. 고칠 내용은 위키의 원본에 반영하고 다시 받습니다.

---

## 3.7 예약 실행

레시피 두 개: **아침 모니터링 브리핑**, **금요일 주간 회고 초안**. 예약은 **담당자 한 명**의 헤르메스에만 등록합니다. 모두가 같은 예약을 걸면 결과가 사람 수만큼 생깁니다.

예약 실행은 게이트웨이가 켜져 있어야 동작합니다(공식 문서 https://hermes-agent.nousresearch.com/docs/user-guide/features/cron). 컴퓨터가 꺼져 있거나 게이트웨이가 멈춰 있으면 실행되지 않습니다.

### 먼저 수동으로 한 번

예약할 내용을 대화로 한 번 실행해 결과를 확인합니다.

```bash
mkdir -p ~/team-ai-agent-code/work/briefing
cd ~/studio-merry-wiki && hermes chat
```

```text
스튜디오 메리의 아침 모니터링 브리핑을 만들어 줘.

먼저 위키 동기화 스킬의 받기 전용 동작으로 위키를 받아 와 줘.
받아 오기에서 멈추면 브리핑을 만들지 말고 멈춘 이유만 기록해 줘.

입력은 ~/team-ai-agent-code/work/input/web-snapshots.md 와
~/team-ai-agent-code/work/output/monitoring.md(이전 결과)야.
새로 확인한 항목, 직접 읽지 못한 항목, 팀이 검토할 질문을 나눠 줘.
이전 결과와 같으면 '변화 없음'이라고 적어 줘.
결과는 ~/team-ai-agent-code/work/briefing/ 에 오늘 날짜(YYYY-MM-DD.md)로 저장해 줘.
외부 메신저에 보내거나 게시하지 마. 위키에 올리지도 마.
```

### 예약 등록

**만들어 보기** — 대화로 등록합니다. 헤르메스가 예약 내용을 보여 주면 확인하고 승인합니다.

```text
방금 한 아침 브리핑을 평일 오전 9시(한국 시간)에 실행하도록 예약해 줘.
위키 동기화 스킬을 붙이고, 작업 폴더는 ~/studio-merry-wiki 로 해 줘.
등록하기 전에 예약 내용·시간대·다음 실행 시각을 보여 줘.
```

**제공 코드로 진행하기** — 명령으로 등록합니다. 작업 폴더는 절대 경로여야 합니다.

```bash
hermes cron create "0 9 * * 1-5" \
  "스튜디오 메리의 아침 모니터링 브리핑을 만들어 줘. (위 수동 실행 지시문의 나머지를 그대로 붙여 넣기)" \
  --skill wiki-sync --workdir "$HOME/studio-merry-wiki" --name "아침 브리핑"
hermes cron list
```

평일만 실행하려면 cron 식 `"0 9 * * 1-5"`를 씁니다. 2026-10-16 기준 장비(헤르메스 v0.22.1)에서 다음 실행 시각이 `+09:00`(한국 시간)으로 계산되는 것을 확인했습니다. 회사 휴일은 cron 식으로 거를 수 없으므로 6.1절에서 다룹니다.

### 실행 확인

게이트웨이를 켜고, 기다리지 않고 한 번 실행해 봅니다.

```bash
hermes gateway            # 다른 Ubuntu 창에서 켜 둠(또는 hermes gateway install)
hermes cron run "아침 브리핑"
ls ~/team-ai-agent-code/work/briefing/
```

- [ ] `hermes cron list`에 예약이 하나만 있고, 스킬과 작업 폴더가 표시됨
- [ ] 실행 후 오늘 날짜 파일이 생김
- [ ] 위키에 기록하지 않은 변경을 일부러 만들어 두고 실행하면, 브리핑 대신 '멈춘 이유'만 남음

### 금요일 회고

같은 순서로 금요일 17시 회고를 만듭니다. 입력은 이번 주 실습 결과 폴더(`~/team-ai-agent-code/work/output`)와 위키 기록(`~/studio-merry-wiki/wiki/log.md`)이고, 결과는 '잘된 점 | 실패한 작업과 원인 | 다음 주에 고칠 한 가지'로 나눕니다. 지시문 첫 줄은 `오늘이 금요일이 아니면 아무것도 하지 말고 끝내.`로 둡니다.

### 제공 코드로 진행하기 — 예약안

예약 내용을 먼저 파일로 검토하고 싶을 때 씁니다. 이 명령은 예약을 **등록하지 않습니다**(status: not_registered).

```bash
cd ~/team-ai-agent-code
python3 run.py run ch03-morning-job --workspace work
python3 run.py run ch03-friday-job --workspace work
cat work/output/morning-job.json
```

**되돌아갈 자리**: 잘못 등록한 예약은 `hermes cron remove "아침 브리핑"`으로 지우고 다시 등록합니다.

---

## 3.8 확장 노트

파이썬으로 간단한 프로그램을 작성해 본 독자를 위한 내용입니다. 건너뛰어도 4장을 시작할 수 있습니다.

### 모델 없이 끝나는 처리

3.2의 소재 정리와 이름 변경은 [../run.py](../run.py)의 `local_task()`가 처리합니다. manifest.json의 `client_id`·`campaign_id`가 비어 있으면 '확인 필요'로 분류하고, 새 이름이 겹치면 충돌로 남깁니다. 자기 팀의 파일명 규칙으로 바꾸려면 이름을 만드는 부분을 고치고 새 작업 폴더에서 `run → check`로 확인합니다.

### 스킬 파일의 형식

스킬은 폴더 하나에 `SKILL.md`가 있는 구조입니다. 맨 위 머리말의 `name`과 `description`이 헤르메스가 스킬을 고르는 기준이므로, `description`에 '언제 쓰는지'를 구체적으로 씁니다. 예: [completed/skills/content-draft/SKILL.md](completed/skills/content-draft/SKILL.md). 확인 항목 하나를 더한 뒤 위키에 올리고, 동료 쪽에서 `hermes skills check`로 변경이 보이는지 확인합니다.

### 위키 동기화 스킬의 실행 파일

[../ch02/wiki-starter/skills/wiki-sync/scripts/wiki_sync.py](../ch02/wiki-starter/skills/wiki-sync/scripts/wiki_sync.py)는 다음을 지킵니다.

- `commit`: 바뀐 파일 목록에 있는 경로만 받음. `.gitignore` 대상은 목록에 나오지 않으므로 기록할 수 없음
- `pull`: 기록하지 않은 변경이 있으면 시작하지 않음. 충돌이면 종료 코드 2로 멈추고 파일 목록을 출력
- `push`: 강제 옵션 없이 실행. 거부되면 멈춤
- `pull-only`: 기록하지 않은 변경·올리지 않은 기록·갈라진 이력 중 하나라도 있으면 아무것도 하지 않음(`git pull --ff-only`)

시험은 `python3 -m unittest discover -s ch02/tests -v`(예제 저장소 루트)로 합니다. 기록 문구 형식을 팀 규칙으로 바꾸고 싶다면 `cmd_commit()`에 검사를 더하고 시험을 하나 추가합니다.

---

## 3장 완료 점검

- [ ] 위키 `guides/`에 SOUL.md와 BB·DP·LB 지침이 있고, 팀원 모두 SOUL.md를 적용함
- [ ] 위키에 봉봉소프트 고객·캠페인 페이지가 출처와 함께 있고, index.md·log.md가 갱신됨
- [ ] 동료가 받은 위키 페이지로 첫 통화 질문을 만듦
- [ ] 스킬 3개가 위키 `skills/`에 있고, 동료가 tap으로 설치함
- [ ] 담당자 한 명의 헤르메스에 예약 2개가 있고, 아침 브리핑이 한 번 실행됨

다음 장: 4장 콘텐츠와 자료 업무(준비 중)
