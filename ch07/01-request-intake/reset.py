"""이 예제 폴더를 받은 처음 상태로 되돌린다.

입력: 이 폴더(git clone으로 받은 code 폴더 안의 예제 폴더)
출력: 고치거나 지운 파일은 받은 내용으로 되살리고, 실습으로 새로 생긴 파일(output 등)은 지운다.
      이 폴더 밖의 파일과 헤르메스 설정(SOUL.md·메모리·스킬·예약)은 바꾸지 않는다.
실행: 헤르메스 대화창에 '작업 폴더는 …야. 이 폴더의 reset.py를 실행해 줘.'라고 부탁한다(터미널에서는 `uv run reset.py`).
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 이 예제가 같은 장 폴더에 따로 만드는 결과 폴더
EXTRA = []


def git(*args):
    try:
        return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 1, "", "git을 찾지 못했습니다.")


def main() -> int:
    # 1. 고치거나 지운 파일을 받은 내용으로 되살린다
    changed = git("diff", "--name-only", "--relative", "HEAD", "--", ".")
    restore = git("restore", "--source=HEAD", "--staged", "--worktree", "--", ".")
    if changed.returncode or restore.returncode:
        print("되돌리지 못했습니다:", (changed.stderr or restore.stderr).strip())
        print("예제를 git clone으로 받았는지 확인하세요(이 책 사용 설명서의 '예제 다운로드').")
        return 1
    # 2. 실습으로 새로 생긴 파일을 지운다(실행 환경 .venv·uv.lock은 남긴다)
    clean = git("clean", "-fdx", "-e", ".venv", "-e", "uv.lock", "--", ".", *EXTRA)
    if clean.returncode:
        print("새로 생긴 파일을 지우지 못했습니다:", clean.stderr.strip())
        return 1
    # 3. 한 일을 보여 준다
    restored, removed = changed.stdout.splitlines(), clean.stdout.splitlines()
    for path in restored:
        print("되살림:", path)
    for line in removed:
        print("지움:", line.removeprefix("Removing "))
    print("처음 상태로 되돌렸습니다." if restored or removed else "이미 처음 상태입니다. 바꾼 것이 없습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
