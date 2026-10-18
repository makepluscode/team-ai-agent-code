# 2장 지침과 회의 자료 정리

저자 편집 합성 입력 8개(텍스트7·문구만 있는 PNG1), 정리7/확인 필요1입니다.
본문 날짜와 attachments.json이 날짜 근거이며 파일 시각이나 이미지 판독은 쓰지 않습니다.

저장소 루트에서 실행합니다.

```bash
uv run team-work prepare --chapter 2 --workspace /tmp/book-ch02
uv run team-work documents organize --confirm --workspace /tmp/book-ch02
uv run team-work verify --workspace /tmp/book-ch02
uv run team-work documents generate --task comparison --workspace /tmp/book-ch02
```

organize는 사람이 input/filing-map.json·filing-reasons.json을 확인한 뒤 제공 대응표로 복사합니다. 모델 판정 결과가 아닙니다.
헤르메스 경로는 prompts/organize.txt로 목록·본문·첨부 목록을 읽어 먼저 제안하고 사람 확인을 기다립니다.
확인한 제안은 output/filing-proposal.json(JSON 객체)에 저장하고 --plan output/filing-proposal.json --confirm으로 복사합니다.
이 경로의 source-map은 실제 복사 기록이며 모델 품질을 자동 판정하지 않습니다.
comparison은 정리본의 두 주간회의만 읽습니다. API 키·모델은 제공 설정을 사용합니다.
완료: 원본8개 해시 보존·정리7/확인 필요1·공통점/변화/제안/미정·파일/절 출처.
새 회의 예제 상용 모델·헤르메스·두 기준 장비 검증과 그림2.3·2.4·2.5 재촬영은 TODO입니다.
