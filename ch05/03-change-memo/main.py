"""5장 변경 메모 예제: 동료의 변경 메모를 raw/에 등록하고 헤르메스의 변경안을 위키에 적용한다.

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서 `uv run main.py [단계]`

단계:
  register: input/의 변경 메모를 raw/에 원본으로 등록(해시 기록)
  apply: output/wiki-draft/의 변경안을 충돌 검사·백업과 함께 wiki/에 적용

제공 코드(team_work)는 ~/team-ai-agent/code에서 찾는다. 다른 곳에 받았다면 환경 변수 TEAM_AGENT_CODE에
그 경로를 지정한다.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = Path(os.environ.get("TEAM_AGENT_CODE", Path.home() / "team-ai-agent" / "code")).expanduser()
NEEDED_VERSION = "1.7"
STEPS = {
    "register": [
        [
            "wiki",
            "register",
            "--source",
            "input/DOC-010_schedule-change.md"
        ]
    ],
    "apply": [
        [
            "wiki",
            "apply-draft"
        ]
    ]
}
DEFAULT = 'register'


def load_team_work():
    # 1. 제공 코드의 위치와 버전을 확인한다
    package = CODE / "src" / "team_work"
    if not package.is_dir():
        sys.exit(f"제공 코드를 찾지 못했습니다: {CODE}\n1.2.3항의 git clone 위치를 확인하거나 TEAM_AGENT_CODE를 지정하세요.")
    sys.path.insert(0, str(CODE / "src"))
    import team_work
    from team_work.cli import main

    if not team_work.__version__.startswith(NEEDED_VERSION):
        sys.exit(f"제공 코드 버전 {team_work.__version__}은 이 예제({NEEDED_VERSION})와 다릅니다. git -C {CODE} pull 뒤 예제를 다시 복사하세요.")
    return main


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if step not in STEPS:
        sys.exit("단계를 고르세요: " + ", ".join(STEPS))
    team_work = load_team_work()
    os.chdir(HERE)  # 상대 경로(input/·output/)는 이 폴더를 기준으로 읽는다
    # 2. 고른 단계의 명령을 차례로 실행한다. 작업 폴더는 이 폴더다
    for command in STEPS[step]:
        args = [part.replace("{extra}", " ".join(sys.argv[2:])) for part in command]
        # 작업 폴더가 필요 없는 명령(평가 등)은 "--no-workspace"로 시작한다
        workspace = [] if args[:1] == ["--no-workspace"] else ["--workspace", str(HERE)]
        args = args[1:] if not workspace else args
        print("$ team-work " + " ".join(args), file=sys.stderr)
        code = team_work([*args, *workspace])
        if code:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
