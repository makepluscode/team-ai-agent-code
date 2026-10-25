"""2장 회의 노트·업무 노트 정리 예제의 결과를 확인한다.

입력: input/files/(원본 12개), output/source-map.json(헤르메스가 쓴 대응표), output/organized/(정리본)
기준: expected/source-map.json(편집한 대응표와 원본 해시)
출력: 화면에 자동 확인 결과와 사람이 확인할 대응표를 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`

이름의 '주제' 부분은 모델마다 표현이 달라도 되므로 날짜·확장자·이름 형식·바이트 일치만 기계로 본다.
종류와 주제가 알맞은지는 사람이 대응표를 보고 판단한다.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected" / "source-map.json"
RESULT = HERE / "output" / "source-map.json"
ORGANIZED = HERE / "output" / "organized"
# YYYY-MM-DD_종류_주제.확장자
NAME_RULE = re.compile(r"^(\d{4}-\d{2}-\d{2})_[^_/]+_[^/]+\.[A-Za-z0-9]+$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["files"]
    problems: list[str] = []

    # 1. 원본 12개가 제공한 상태 그대로인지 확인한다
    for item in expected:
        source = HERE / item["source"]
        if not source.exists() or sha256(source) != item["sha256"]:
            problems.append(f"원본이 없거나 바뀌었습니다: {item['source']}")
    if not problems:
        print(f"[통과] 원본 {len(expected)}개 보존")

    # 2. 헤르메스가 쓴 대응표를 읽는다
    if not RESULT.exists():
        print("[실패] output/source-map.json이 없습니다. 대응표 저장까지 마쳤는지 확인하세요.")
        return 1
    try:
        rows = json.loads(RESULT.read_text(encoding="utf-8"))["files"]
    except (json.JSONDecodeError, KeyError, TypeError):
        print('[실패] output/source-map.json의 형식이 지시문과 다릅니다({"files": [...]}).')
        print("  → 다음에 할 일: 같은 대화에서 지시문 4번의 형식대로 output/source-map.json을 다시 저장해 달라고 요청한 뒤 uv run check.py를 다시 실행합니다.")
        return 1
    by_source = {}
    for row in rows:
        # 절대 경로로 적어도 input/files/ 뒤의 이름으로 맞춘다
        source = str(row.get("source", ""))
        if "input/files/" in source:
            source = "input/files/" + source.split("input/files/", 1)[1]
        by_source.setdefault(source, []).append(row)

    # 3. 원본마다 대응표의 줄이 하나씩 있고, 상태와 정리본이 기준과 맞는지 본다
    mapped_copies = set()
    for item in expected:
        found = by_source.get(item["source"], [])
        if len(found) != 1:
            problems.append(f"대응표에 {item['source']} 줄이 {len(found)}개입니다(1개여야 함)")
            continue
        row = found[0]
        if str(row.get("copy")).strip().lower() in ("null", "none", ""):
            row["copy"] = None  # "null"을 문자열로 적은 대응표도 정리본 없음으로 읽는다
        if row.get("status") != item["status"]:
            problems.append(f"{item['source']}: 상태 {row.get('status')} (기준 {item['status']})")
            continue
        if item["status"] == "duplicate":
            if row.get("copy"):
                problems.append(f"{item['source']}: 중복 파일은 정리본을 만들지 않습니다")
            continue
        copy = HERE / str(row.get("copy", ""))
        if not copy.is_file():
            problems.append(f"{item['source']}: 정리본이 없습니다 ({row.get('copy')})")
            continue
        mapped_copies.add(copy.resolve())
        if sha256(copy) != item["sha256"]:
            problems.append(f"{row['copy']}: 원본과 내용이 다릅니다")
        if item["status"] == "needs_review":
            if copy.parent.name != "확인-필요" or copy.name != Path(item["source"]).name:
                problems.append(f"{item['source']}: 확인-필요/에 원래 이름으로 보존해야 합니다")
            continue
        match = NAME_RULE.match(copy.name)
        want_date = Path(item["copy"]).name[:10]
        if copy.parent != ORGANIZED:
            problems.append(f"{row['copy']}: output/organized/ 바로 아래에 있어야 합니다")
        if not match:
            problems.append(f"{row['copy']}: 이름이 YYYY-MM-DD_종류_주제.확장자 형식이 아닙니다")
        elif match.group(1) != want_date:
            problems.append(f"{row['copy']}: 날짜 {match.group(1)} (근거 날짜 {want_date})")
        if copy.suffix != Path(item["source"]).suffix:
            problems.append(f"{row['copy']}: 확장자가 원본과 다릅니다")

    # 4. 대응표에 없는 파일이 정리본 폴더에 섞이지 않았는지 본다
    if ORGANIZED.exists():
        extra = [
            p for p in ORGANIZED.rglob("*") if p.is_file() and p.resolve() not in mapped_copies
        ]
        problems += [f"대응표에 없는 파일: {p.relative_to(HERE)}" for p in extra]

    for line in problems:
        print(f"[실패] {line}")
    if problems:
        print("  → 다음에 할 일: 같은 대화에서 [실패] 줄을 보여 주고 대응표와 정리본을 고쳐 달라고 요청한 뒤 uv run check.py를 다시 실행합니다.")
        print("    처음부터 다시 하려면 uv run reset.py로 결과 폴더를 지웁니다. 원본이 바뀌었으면 git restore input으로 받은 상태로 되돌립니다.")
    if not problems:
        print("[통과] 정리본 10개·중복 1개·확인 필요 1개, 이름 형식·날짜·바이트 일치")

    # 5. 종류와 주제의 적절성은 사람이 판단한다
    print("\n사람이 확인할 대응표(종류·주제가 알맞은가, 근거가 원본에 있는가):")
    for row in rows:
        target = row.get("copy") or "(정리본 없음)"
        print(f"- {row.get('source')} → {target} [{row.get('status')}] {row.get('date_basis', '')}")

    print("\n자동 확인:", "통과" if not problems else f"실패 {len(problems)}건")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
