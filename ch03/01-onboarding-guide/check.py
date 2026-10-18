"""3장 온보딩 가이드 예제의 결과를 확인한다.

입력: input/DOC-001_onboarding.md(원본), output/DOC-007_onboarding-guide.r1.md(헤르메스가 저장한 결과)
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`
"""

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "output" / "DOC-007_onboarding-guide.r1.md"
# 제공한 원본과 SHA-256
SOURCES = {
    "input/DOC-001_onboarding.md": "ae5f61026f5286dcad9cb41e791edc9b4cd05585b1ba8300b9cf9ecb3cd2e58d",
}
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = [
    ("첫 일정이 '잠정'으로 남았는가", ("잠정",)),
    ("장소·최종 검토자·세부 시간표가 '미정'으로 남았는가", ("미정",)),
    ("출처(DOC-001, 문서 버전 r1)가 적혔는가", ("DOC-001",)),
]
# 표현으로 찾기 어려워 질문만 보여 주는 항목
HUMAN_ONLY = [
    "원본에 없는 장소·검토자·확정 일정을 채워 넣지 않았는가",
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
    for question in HUMAN_ONLY:
        print(f"- {question}")

    print("\n자동 확인:", "통과" if failures == 0 else f"실패 {failures}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
