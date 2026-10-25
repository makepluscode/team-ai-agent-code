"""이 예제 폴더의 실습 결과(output/)를 지워 처음부터 다시 할 수 있게 한다.

입력: 이 폴더의 output/
출력: output/ 폴더를 지운다. 받은 원본(input/)·지시문·헤르메스 설정(~/.hermes의 SOUL.md·메모리·스킬·예약)은 바꾸지 않는다.
실행: 이 폴더에서 `uv run reset.py`(지울 파일 수를 보여 주고 y/N을 묻는다), 묻지 않으려면 `uv run reset.py --yes`
"""

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "output"


def main() -> int:
    # 1. 지울 결과가 있는지 확인한다
    if not OUTPUT.exists():
        print("output/이 없습니다. 이미 처음 상태입니다.")
        return 0
    files = [p for p in OUTPUT.rglob("*") if p.is_file()]
    print(f"지울 결과: output/ (파일 {len(files)}개)")
    for path in files[:10]:
        print(f"  - {path.relative_to(HERE)}")
    if len(files) > 10:
        print(f"  … 외 {len(files) - 10}개")

    # 2. 사람에게 묻고 지운다
    if "--yes" not in sys.argv[1:]:
        answer = input("남겨 둘 결과는 먼저 예제 폴더 밖에 복사하세요. 지울까요? [y/N] ").strip().lower()
        if answer != "y":
            print("지우지 않았습니다.")
            return 1
    shutil.rmtree(OUTPUT)
    print("output/을 지웠습니다. 헤르메스 설정(~/.hermes)은 그대로입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
