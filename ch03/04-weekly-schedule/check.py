"""3장 주간 보고 예약 예제의 결과를 확인한다.

입력: input/organized/(회의 노트·업무 노트 정리본 8개), input/DOC-004_weekly-meetings.md, input/snapshot.json
결과: output/scheduled/오늘날짜_DOC-009_weekly-report.r1.md(예약이 오늘 남긴 보고)
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py` (다른 날의 결과는 `uv run check.py 2026-10-23`처럼 날짜를 넘긴다)
"""

import hashlib
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 제공한 원본과 SHA-256
SOURCES = {
    "input/DOC-004_weekly-meetings.md": "6b7964eb758bd13149cf7e6361761db31928e201f6f75bca44ed2fe6af1ee7a7",
    "input/organized/2026-10-02_회의노트_주간회의.md": "4cc501917c74b057ad9990eed11e8fae6850805c3f973477d65d25697913445f",
    "input/organized/2026-10-05_업무노트_할일.txt": "98ec89ace2353f88154f84bc1c7bee57903fdbb4645396904f286ca7deba57f0",
    "input/organized/2026-10-05_회의노트_주간회의.md": "09608240752cdb5c48b3fb45bb09ffd3bad75652b1b0999f4ac415e810f1af1c",
    "input/organized/2026-10-06_대화기록_온보딩준비.txt": "ba1c96b191c1fdf8b19cd5c8f7766d726285d1d6afafddb3a249bd6ed720f6dc",
    "input/organized/2026-10-06_업무노트_비교표작성.md": "7b96c12336ef17f827588efc94cc30962a33726106bd0a8202f2c3d82ce8ef99",
    "input/organized/2026-10-06_업무노트_회의실문의.txt": "c0306db9ea7a3df6862d789b4481e3bef8aa6e048ab782ee01fa6f667edcd189",
    "input/organized/2026-10-06_회의노트_원온원.txt": "d5fc21fa6ec23628b77cf7ccceed2de5a4d26835313a0ca53d9e8ff6a9076d15",
    "input/organized/2026-10-07_업무노트_준비상태점검.txt": "933028553f258c08a1b0d41b472377727eab07c1f0843bab8af1aeedb01c69f1",
    "input/snapshot.json": "55cae40a6f04c5bbeca0f3bdb1996f69a83e2ba11463c7b69739672df072e116",
}
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = [
    (
        "관측 기준 시각이 input/snapshot.json의 값(2026-10-07 09:00) 그대로인가",
        ("관측 기준", "2026-10-07"),
    ),
    (
        "완료가 항목키 ITEM-001~004의 네 건이고, 대화의 재언급을 다시 세지 않았는가",
        ("ITEM-001", "ITEM-002", "ITEM-003", "ITEM-004"),
    ),
    ("ITEM-005·006이 완료가 아니라 제안·상태 미기재로 남았는가", ("ITEM-005", "ITEM-006")),
    ("보고 업무 TASK-001이 '확인 대기'인가", ("TASK-001",)),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_result() -> Path | None:
    # 예약 실행은 실행 날짜를 붙인 새 파일을 남긴다. 예전 결과로 통과하지 않게 기본은 오늘 날짜 파일만 본다.
    # 다음 날 확인할 때는 날짜를 넘긴다: uv run check.py 2026-10-23
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    path = HERE / "output" / "scheduled" / f"{day}_DOC-009_weekly-report.r1.md"
    if not path.exists():
        found = sorted((HERE / "output" / "scheduled").glob("*_DOC-009_weekly-report.r1.md"))
        if found:
            print(f"    → {day} 결과가 없습니다. 있는 결과: {', '.join(f.name[:10] for f in found)}. "
                  "그날 결과를 확인하려면 uv run check.py <날짜>")
        return None
    return path


def main() -> int:
    failures = 0

    # 1. 원본이 제공한 상태 그대로인지 확인한다
    changed = [
        name
        for name, digest in SOURCES.items()
        if not (HERE / name).exists() or sha256(HERE / name) != digest
    ]
    for name in changed:
        print(f"[실패] 원본이 없거나 바뀌었습니다: {name}")
    failures += len(changed)
    if not changed:
        print(f"[통과] 원본 {len(SOURCES)}개 보존")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    result = find_result()
    if result is None or not result.read_text(encoding="utf-8").strip():
        print(
            "[실패] 오늘 날짜의 결과 파일이 없거나 비어 있습니다: output/scheduled/오늘날짜_DOC-009_weekly-report.r1.md"
        )
        return 1
    print(f"[통과] 결과 파일 저장: {result.relative_to(HERE)}")
    text = result.read_text(encoding="utf-8")

    # 3. 사람이 대조할 자리를 보여 준다. 표현이 있다고 내용이 맞다는 뜻은 아니다
    print("\n사람이 확인할 항목(expected/의 비교용 결과·원본과 대조):")
    for question, words in HUMAN_CHECKS:
        lines = [line.strip() for line in text.splitlines() if any(w in line for w in words)]
        print(f"- {question}")
        for line in lines[:4] or ["(해당 표현이 있는 줄이 없습니다. 파일을 열어 확인하세요.)"]:
            print(f"    {line[:120]}")

    print("\n자동 확인:", "통과" if failures == 0 else f"실패 {failures}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
