"""9장 검토 예제: 사람의 검토 6건을 기록하고 TASK-002를 재검토 경로로 완료한다.

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서 `uv run main.py [단계]`

단계:
  setup: 기록 DB 준비
  review: 검토 6건 기록(사람 확인 표시를 포함하므로 결과를 읽은 뒤 실행)
  task-002: TASK-002: 확인 대기 → 수정 필요 → 진행 → 확인 대기 → 완료
  list: 요청·업무 목록 출력

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
    "setup": [
        [
            "requests",
            "init"
        ]
    ],
    "review": [
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-001.json",
            "--actor",
            "M01",
            "--human-confirmed"
        ],
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-002.json",
            "--actor",
            "M01",
            "--human-confirmed"
        ],
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-003.json",
            "--actor",
            "M01",
            "--human-confirmed"
        ],
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-004.json",
            "--actor",
            "M05",
            "--human-confirmed"
        ],
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-005.json",
            "--actor",
            "M01",
            "--human-confirmed"
        ],
        [
            "requests",
            "review",
            "--input",
            "input/reviews/REV-006.json",
            "--actor",
            "M01",
            "--human-confirmed"
        ]
    ],
    "task-002": [
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-002",
            "--status",
            "수정 필요",
            "--actor",
            "M01",
            "--reason",
            "회의 확정 일정으로 수정 요청(REV-001)",
            "--source-ref",
            "raw/DOC-012_r1.md#decision-01",
            "--expected",
            "확인 대기"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-002",
            "--status",
            "진행",
            "--actor",
            "M02",
            "--reason",
            "수정 시작",
            "--source-ref",
            "raw/DOC-012_r1.md#decision-01",
            "--expected",
            "수정 필요"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-002",
            "--status",
            "확인 대기",
            "--actor",
            "M02",
            "--reason",
            "DOC-007 r3 수정 완료, 재검토 요청",
            "--source-ref",
            "output/DOC-007_r3.md#schedule",
            "--expected",
            "진행"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-002",
            "--status",
            "완료",
            "--actor",
            "M01",
            "--human-confirmed",
            "--reason",
            "재검토 뒤 확정 일정 반영 확인",
            "--source-ref",
            "output/DOC-007_r3.md#schedule",
            "--expected",
            "확인 대기"
        ]
    ],
    "list": [
        [
            "requests",
            "list"
        ]
    ]
}
DEFAULT = 'setup'


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
