"""2장 두 주간회의 비교 예제의 결과를 확인한다.

입력: input/의 두 주간회의 노트(원본), output/DOC-006_comparison.md(헤르메스가 저장한 비교표)
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`
"""

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "output" / "DOC-006_comparison.md"
# 제공한 원본과 SHA-256
SOURCES = {
    "input/2026-10-02_회의노트_주간회의.md": "f582fd23234d57a1a72cccd7c5d5717588fce17e41fadb42221e9d1de8942ed8",
    "input/2026-10-05_회의노트_주간회의.md": "634cf8aacca8ece123e65fb2abca30e21f9e044b90c806b0281d4768b8b848cc",
}
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = [
    (
        "두 노트의 출처(파일명·절 제목 또는 항목키)가 사실 옆에 적혔는가",
        ("2026-10-02", "2026-10-05"),
    ),
    ("최신 경로 병기 의견이 결정이 아니라 제안으로 남았는가", ("제안",)),
    ("장소·최종 검토자가 '미정'으로 남았는가", ("미정",)),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures = 0

    # 1. 원본이 제공한 상태 그대로인지 확인한다
    for name, digest in SOURCES.items():
        path = HERE / name
        if path.exists() and sha256(path) == digest:
            print(f"[통과] 원본 보존: {name}")
        else:
            print(f"[실패] 원본이 없거나 바뀌었습니다: {name}")
            failures += 1

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    if not RESULT.exists() or not RESULT.read_text(encoding="utf-8").strip():
        print(f"[실패] 결과 파일이 없거나 비어 있습니다: {RESULT.relative_to(HERE)}")
        return 1
    print(f"[통과] 결과 파일 저장: {RESULT.relative_to(HERE)}")
    text = RESULT.read_text(encoding="utf-8")

    # 3. 사람이 대조할 자리를 보여 준다. 표현이 있다고 내용이 맞다는 뜻은 아니다
    print("\n사람이 확인할 항목(원본과 대조):")
    for question, words in HUMAN_CHECKS:
        lines = [line.strip() for line in text.splitlines() if any(w in line for w in words)]
        print(f"- {question}")
        for line in lines[:3] or ["(해당 표현이 있는 줄이 없습니다. 파일을 열어 확인하세요.)"]:
            print(f"    {line}")

    print("\n자동 확인:", "통과" if failures == 0 else f"실패 {failures}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
