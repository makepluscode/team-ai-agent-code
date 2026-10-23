"""이 예제 폴더를 받은 처음 상태로 되돌린다.

입력: 이 폴더(받은 code 저장소 안의 예제 폴더)와 저장소의 변경 이력
출력: 실습으로 생긴 파일(output/·state/ 등)을 지우고, 바뀐 제공 파일(wiki/·raw/ 등)을 받은 내용으로 되돌린다.
      헤르메스 설정(~/.hermes의 SOUL.md·메모리·스킬·예약)은 바꾸지 않는다.
실행: 이 폴더에서 `uv run reset.py`(지울·되돌릴 목록을 보여 주고 y/N을 묻는다), 묻지 않으려면 `uv run reset.py --yes`
"""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 이 예제가 폴더 밖(같은 장 폴더 안)에 만드는 결과 폴더
EXTRA = ["../03-hours-backup-backup", "../03-hours-backup-restored"]
# 실행 환경(uv가 만드는 파일)은 지우지 않는다
KEEP = {".venv", "uv.lock"}


def git(*args):
    try:
        return subprocess.run(["git", "-C", str(HERE), *args], capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:  # git이 설치되지 않은 경우
        return subprocess.CompletedProcess(args, 1, "", "git을 찾지 못했습니다")


def main() -> int:
    # 1. 받은 code 저장소의 예제 폴더인지 확인한다(다른 저장소 안에 풀어 둔 폴더는 건드리지 않는다)
    top = git("rev-parse", "--show-toplevel")
    prefix = git("rev-parse", "--show-prefix")
    if top.returncode or prefix.returncode or Path(top.stdout.strip()).resolve() != HERE.parents[1] \
            or git("cat-file", "-e", f"HEAD:{prefix.stdout.strip()}README.md").returncode:
        print("이 폴더는 git clone으로 받은 code 폴더의 예제 폴더가 아니어서 되돌릴 수 없습니다(1.2.3항 예제 다운로드).\n"
              "git이 설치돼 있는지(git --version) 확인하고, 압축 파일로 받았다면 git clone으로 다시 받으세요.")
        return 1
    prefix = prefix.stdout.strip()
    # 2. 바뀐 파일과 새로 생긴 파일을 모은다(-z: 한글·공백이 든 경로도 그대로 받는다)
    status = git("status", "--porcelain", "-z", "--untracked-files=all", "--ignored", "--", ".")
    if status.returncode:
        print("파일 상태를 읽지 못해 멈춥니다:", status.stderr.strip())
        return 1
    changed, created = [], []
    for line in filter(None, status.stdout.split("\0")):
        code, path = line[:2], line[3:]
        if code[0] not in " ?!":  # git add·이름 바꾸기처럼 직접 Git으로 등록한 변경은 여기서 되돌리지 않는다
            print(f"Git에 등록(스테이지)된 변경이 있어 멈춥니다: {path}\n"
                  "이 책의 실습에서는 생기지 않는 상태입니다. 직접 Git 명령을 썼다면 그 변경을 먼저 정리하세요.")
            return 1
        relative = path[len(prefix):] if path.startswith(prefix) else path
        if relative.split("/")[0] in KEEP:
            continue
        (created if code in {"??", "!!"} else changed).append(relative)
    extra = [HERE / p for p in EXTRA if (HERE / p).exists()]
    if not (changed or created or extra):
        print("이미 받은 처음 상태입니다. 바꿀 것이 없습니다.")
        return 0
    # 3. 무엇을 되돌리고 지우는지 보여 주고 사람에게 묻는다
    for title, items in (("되돌릴 제공 파일", changed), ("삭제할 추가 파일", created),
                         ("지울 결과 폴더", [p.name for p in extra])):
        if items:
            print(f"{title} {len(items)}개:")
            for item in items[:20]:
                print(f"  {item}")
            if len(items) > 20:
                print(f"  … 외 {len(items) - 20}개")
    if "--yes" not in sys.argv:
        try:
            answer = input("직접 고친 내용도 함께 사라집니다. 처음 상태로 되돌릴까요? [y/N] ")
        except (EOFError, OSError):
            answer = ""
        if answer.strip().lower() not in {"y", "yes", "예", "네"}:
            print("되돌리지 않았습니다.")
            return 1
    # 4. 제공 파일은 받은 내용으로 되돌리고, 실습 결과는 지운다
    if changed:
        result = git("checkout", "HEAD", "--", ".")
        if result.returncode != 0:
            print(result.stderr.strip())
            return 1
    for relative in created:
        target = HERE / relative
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    for target in extra:
        shutil.rmtree(target)
    # 5. 비게 된 폴더를 정리한다
    for folder in sorted((p for p in HERE.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if KEEP & set(folder.relative_to(HERE).parts):  # 실행 환경 안은 건드리지 않는다
            continue
        if not any(folder.iterdir()) and not git("ls-files", "--", str(folder)).stdout:
            folder.rmdir()
    print("처음 상태로 되돌렸습니다. README.md의 실행 방법 첫 단계부터 다시 하세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
