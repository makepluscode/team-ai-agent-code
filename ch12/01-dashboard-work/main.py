"""12장 대시보드 작업 예제: 새 요청을 접수하고 쓰기 대시보드와 상태 전이를 기록한다.

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서 `uv run main.py [단계]`

단계:
  setup: 기록 DB 준비(10/19 기준 공동 기록)
  intake: 화면 대신 파일로 새 요청 REQ-011 접수
  serve: 입력·상태 변경이 가능한 대시보드(http://127.0.0.1:8000)
  task-013: TASK-013 상태 전이 6단계(진행 → … → 완료, 완료는 사람 확인)
  json: 저장된 모든 필드를 JSON으로 출력
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
    "intake": [
        [
            "requests",
            "intake",
            "--input",
            "input/dashboard-request.json"
        ]
    ],
    "serve": [
        [
            "dashboard",
            "--writable"
        ]
    ],
    "task-013": [
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "진행",
            "--actor",
            "M02",
            "--reason",
            "초안 작성 시작",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--expected",
            "접수"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "확인 대기",
            "--actor",
            "M02",
            "--reason",
            "사람 확인과 수정 이유를 남긴 합성 사례",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--expected",
            "진행"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "수정 필요",
            "--actor",
            "M01",
            "--reason",
            "사람 확인과 수정 이유를 남긴 합성 사례",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--expected",
            "확인 대기"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "진행",
            "--actor",
            "M02",
            "--reason",
            "사람 확인과 수정 이유를 남긴 합성 사례",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--expected",
            "수정 필요"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "확인 대기",
            "--actor",
            "M02",
            "--reason",
            "사람 확인과 수정 이유를 남긴 합성 사례",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--expected",
            "진행"
        ],
        [
            "requests",
            "transition",
            "--task-id",
            "TASK-013",
            "--status",
            "완료",
            "--actor",
            "M01",
            "--reason",
            "사람 확인과 수정 이유를 남긴 합성 사례",
            "--source-ref",
            "input/dashboard-request.json#REQ-011",
            "--human-confirmed",
            "--expected",
            "확인 대기"
        ]
    ],
    "json": [
        [
            "requests",
            "list",
            "--json"
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
