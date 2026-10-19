"""헤르메스 한 대로 모으기 예제의 결과를 확인한다.

입력: .exercise.json(이 예제가 제공한 원본의 기준 해시)
결과: output/consolidation-check.md
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
RESULTS = ["output/consolidation-check.md"]
# SQLite 기록 확인: (설명, 질의, 기대 개수)
COUNTS = [["공동 기록의 요청", "SELECT COUNT(*) FROM requests", 10], ["공동 기록의 업무", "SELECT COUNT(*) FROM tasks", 12]]
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hint(name: str) -> str:
    """빠진 결과 파일마다 다음에 할 일을 알려 준다."""
    if name == "output/wiki-base.json":
        return "변경안을 uv run main.py preview로 확인한 뒤 uv run main.py apply로 적용하세요."
    if name.startswith("raw/"):
        return "uv run main.py register로 원본을 등록하세요."
    if name.startswith("wiki/"):
        return "헤르메스 변경안(output/wiki-draft/)을 확인하고 적용했는지 보세요(uv run main.py로 할 일 확인)."
    if name.startswith("../"):
        return "uv run main.py backup과 uv run main.py restore를 실행했는지 보세요."
    return "헤르메스 지시문을 실행해 이 이름으로 저장했는지 보세요. 다른 이름으로 저장됐다면 지시문의 저장 경로를 확인합니다."


def main() -> int:
    failures = 0

    # 1. 제공한 원본(input/·raw/)이 그대로인지 확인한다
    sources = json.loads((HERE / ".exercise.json").read_text(encoding="utf-8"))["sources"]
    changed = [name for name, digest in sources.items()
               if not (HERE / name).is_file() or sha256(HERE / name) != digest]
    for name in changed:
        print(f"[실패] 원본이 없거나 바뀌었습니다: {name}")
    if changed:
        print("    → 원본은 고치지 않습니다. 장 폴더를 새 이름으로 다시 복사해 시작하세요.")
    failures += len(changed)
    if not changed:
        print(f"[통과] 원본 {len(sources)}개 보존")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    texts = []
    for name in RESULTS:
        path = HERE / name
        try:
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
        except UnicodeDecodeError:  # DB 같은 이진 파일은 비어 있지 않은지만 본다
            text = "" if not path.stat().st_size else None
        if text is None or text.strip():
            print(f"[통과] 결과 파일 저장: {name}")
            texts.append(text or "")
        else:
            print(f"[실패] 결과 파일이 없거나 비어 있습니다: {name}")
            print(f"    → {hint(name)}")
            failures += 1

    # 3. 기록 DB의 건수를 확인한다
    database = HERE / "state" / "requests.sqlite3"
    for label, query, expected in COUNTS:
        if not database.exists():
            print(f"[실패] 기록 DB가 없습니다: {label}")
            print("    → uv run main.py로 할 일을 보고 setup(또는 intake) 단계를 먼저 실행하세요.")
            failures += 1
            continue
        with sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True) as db:
            actual = db.execute(query).fetchone()[0]
        mark = "통과" if actual == expected else "실패"
        failures += mark == "실패"
        print(f"[{mark}] {label}: {actual}건 (기준 {expected}건)")
        if mark == "실패":
            print("    → uv run main.py로 아직 실행하지 않은 단계를 확인하세요. 결과를 보려면 uv run main.py list")

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
