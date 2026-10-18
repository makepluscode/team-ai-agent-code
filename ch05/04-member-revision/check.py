"""위키를 받은 동료의 결과 수정 예제의 결과를 확인한다.

입력: .exercise.json(이 예제가 제공한 원본의 기준 해시)
결과: output/DOC-007_onboarding-guide.r2.md
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 있어야 하는 결과 파일(이 폴더 기준)
RESULTS = ["output/DOC-007_onboarding-guide.r2.md"]
# SQLite 기록 확인: (설명, 질의, 기대 개수)
COUNTS = []
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = [["안내 날짜 10월 15일 확정, 시각·장소·검토자 미정인가", ["10월 15일", "2026-10-15", "미정"]], ["supersedes DOC-007@r1과 근거 DOC-010@r1이 적혔는가", ["supersedes", "DOC-010@r1"]], ["업무 TASK-002가 '확인 대기'인가", ["TASK-002", "확인 대기"]]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures = 0

    # 1. 제공한 원본(input/·raw/)이 그대로인지 확인한다
    sources = json.loads((HERE / ".exercise.json").read_text(encoding="utf-8"))["sources"]
    changed = [name for name, digest in sources.items()
               if not (HERE / name).is_file() or sha256(HERE / name) != digest]
    for name in changed:
        print(f"[실패] 원본이 없거나 바뀌었습니다: {name}")
    failures += len(changed)
    if not changed:
        print(f"[통과] 원본 {len(sources)}개 보존")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    texts = []
    for name in RESULTS:
        path = HERE / name
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            print(f"[통과] 결과 파일 저장: {name}")
            texts.append(path.read_text(encoding="utf-8"))
        else:
            print(f"[실패] 결과 파일이 없거나 비어 있습니다: {name}")
            failures += 1

    # 3. 기록 DB의 건수를 확인한다
    database = HERE / "state" / "requests.sqlite3"
    for label, query, expected in COUNTS:
        if not database.exists():
            print(f"[실패] 기록 DB가 없습니다. 먼저 uv run main.py를 실행하세요: {label}")
            failures += 1
            continue
        with sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True) as db:
            actual = db.execute(query).fetchone()[0]
        mark = "통과" if actual == expected else "실패"
        failures += mark == "실패"
        print(f"[{mark}] {label}: {actual}건 (기준 {expected}건)")

    # 4. 사람이 대조할 자리를 보여 준다. 표현이 있다고 내용이 맞다는 뜻은 아니다
    if HUMAN_CHECKS:
        print("\n사람이 확인할 항목(원본·expected/와 대조):")
        text = "\n".join(texts)
        for question, words in HUMAN_CHECKS:
            print(f"- {question}")
            lines = [line.strip() for line in text.splitlines() if any(w in line for w in words)]
            for line in lines[:3]:
                print(f"    {line[:120]}")

    print("\n자동 확인:", "통과" if failures == 0 else f"실패 {failures}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
