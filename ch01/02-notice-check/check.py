"""1장 안내문 점검 예제의 결과를 확인한다.

입력: input/(안내문 초안·온보딩 자료·자료함 사본, 원본), output/DOC-005_notice-check.md(헤르메스가 저장한 점검표)
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`
"""

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "output" / "DOC-005_notice-check.md"
# 제공한 원본과 SHA-256. 자료함(input/shared/)의 파일을 옮기거나 더해도 실패로 본다
SOURCES = {
    "input/DOC-001_onboarding.md": "ae5f61026f5286dcad9cb41e791edc9b4cd05585b1ba8300b9cf9ecb3cd2e58d",
    "input/DOC-015_notice-draft.md": "f0a3c7e477a8e7f7b590fd19d57e25541069ff7c7c4ed7e360226bfd20f9ceb1",
    "input/shared/archive/DOC-003_notice-retro.md": "eb6dd72e963558ced837415d28a134fa95fb07e0e65b3af90a4d9e4a25e80323",
    "input/shared/rules/DOC-002_library-rules.md": "7ba1c8734df98eeb8b9d57500a32cafa7e0ecdedf71fc15369f339b8c5152756",
    "input/shared/team/team-intro_v1.md": "aa18f9849819208530d8d58d851b774b530b584f41543d00a90537377be88cae",
    "input/shared/team/team-intro_v2.md": "b9c5de9e53297afca5d9e6efa376de47c03d394623aa82e1d67b21b3c2572bc1",
    "input/shared/tools/accounts-guide.md": "93d5827422b436a7175faab7e7298f6fddb34aca139d12201e981fc911a13084",
}
# 안내문의 경로마다 저자가 확인한 상태. 점검표의 해당 줄과 사람이 대조한다
EXPECTED = [
    ("team-intro_v1.md", "옛 버전(같은 폴더의 team-intro_v2.md가 대체)"),
    ("accounts-guide.md", "정상"),
    ("DOC-002_library-rules.md", "정상"),
    ("DOC-003_notice-retro.md", "위치 다름(shared/archive/에 있음)"),
    ("question-list.md", "없음"),
]
# 일정·장소 대조에서 볼 표현
HUMAN_CHECKS = [
    ("일정이 원본대로 '잠정'이라고 지적했는가", ("잠정",)),
    ("장소 '회의실 A'가 원본에 없는(미정) 값이라고 지적했는가", ("회의실 A", "미정")),
]
# 표현으로 찾기 어려워 질문만 보여 주는 항목
HUMAN_ONLY = [
    "상태마다 '실제로 확인한 내용'이 파일 목록이나 파일 내용에 근거하는가(추측이 아닌가)",
    "제안이 '제안:'으로 시작해 확인한 사실과 구별돼 있는가",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def show(text: str, words: tuple) -> None:
    lines = [line.strip() for line in text.splitlines() if any(w in line for w in words)]
    for line in lines[:3] or ["(해당 표현이 있는 줄이 없습니다. 파일을 열어 확인하세요.)"]:
        print(f"    {line}")


def main() -> int:
    failures = 0

    # 1. 원본과 자료함이 제공한 상태 그대로인지 확인한다(내용·추가·이동)
    for name, digest in SOURCES.items():
        path = HERE / name
        if path.exists() and sha256(path) == digest:
            print(f"[통과] 원본 보존: {name}")
        else:
            print(f"[실패] 원본이 없거나 바뀌었습니다: {name}")
            failures += 1
    extra = sorted(str(p.relative_to(HERE)) for p in (HERE / "input").rglob("*") if p.is_file())
    extra = [name for name in extra if name not in SOURCES]
    for name in extra:
        print(f"[실패] 자료함에 없던 파일이 생겼습니다: {name}")
        failures += 1
    if failures:
        print("  다음: uv run reset.py로 예제 폴더를 처음 상태로 되돌린 뒤 다시 시작합니다.")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    if not RESULT.exists() or not RESULT.read_text(encoding="utf-8").strip():
        print(f"[실패] 결과 파일이 없거나 비어 있습니다: {RESULT.relative_to(HERE)}")
        print("  다음: 같은 대화에서 'output/DOC-005_notice-check.md로 저장하고 다시 읽어 보여 줘'라고 요청합니다.")
        return 1
    print(f"[통과] 결과 파일 저장: {RESULT.relative_to(HERE)}")
    text = RESULT.read_text(encoding="utf-8")

    # 3. 사람이 대조할 자리를 보여 준다. 표현이 있다고 내용이 맞다는 뜻은 아니다
    print("\n사람이 확인할 항목(저자가 확인한 상태와 대조):")
    for name, expected in EXPECTED:
        print(f"- {name} → 저자 확인: {expected}")
        show(text, (name,))
    for question, words in HUMAN_CHECKS:
        print(f"- {question}")
        show(text, words)
    for question in HUMAN_ONLY:
        print(f"- {question}")

    print("\n자동 확인:", "통과" if failures == 0 else f"실패 {failures}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
