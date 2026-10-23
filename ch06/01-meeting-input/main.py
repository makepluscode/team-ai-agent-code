"""6장 회의 입력 예제: 음원이 있을 때 faster-whisper로 로컬 전사한다(선택).

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서
  uv run main.py            지금 할 일과 단계 목록(아무것도 실행하지 않음)
  uv run main.py <단계>     단계 실행. 사람 확인이 필요한 단계는 내용을 보여 주고 y/N을 묻는다
  uv run main.py <단계> --yes   확인 질문만 생략(충돌·원본 검사는 그대로)

단계:
  transcribe: 음원을 로컬 전사해 output/transcript.json에 저장(uv run --extra transcription main.py transcribe <음원>)

제공 코드(team_work)는 이 예제 폴더가 들어 있는 code 폴더에서 찾는다. 예제 폴더를 다른 곳으로 옮겼다면
환경 변수 TEAM_AGENT_CODE에 받은 code 폴더 경로를 지정한다. 단계의 실제 처리는 code/src/team_work/에 있고, 이 파일은 단계 이름과 명령을 잇기만 한다.
"""

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 예제 폴더(code/chNN/NN-이름)의 두 단계 위가 받은 code 폴더다. 다른 곳에서 쓸 때만 TEAM_AGENT_CODE를 지정한다
CODE = Path(os.environ.get("TEAM_AGENT_CODE", HERE.parents[1])).expanduser()
NEEDED_VERSION = "1.7"
# 단계 이름 → 설명과 team-work 명령 목록
STEPS = {
    "transcribe": [
        "음원을 로컬 전사해 output/transcript.json에 저장(uv run --extra transcription main.py transcribe <음원>)",
        [
            [
                "meetings",
                "transcribe",
                "--audio",
                "{extra}"
            ]
        ]
    ]
}
# 한 번 실행할 때 명령 하나씩 진행하는 단계(진행 위치는 state/progress.json)
ONE_AT_A_TIME = []
# 명령을 실행하기 전에 보여 줄 파일(사람이 확인할 내용)
SHOW = {}
# 책의 실행 순서와, 끝났는지 알 수 있는 파일(없으면 빈 목록)
GUIDE = [
    [
        "hermes chat --query-file prompt.md",
        []
    ],
    [
        "uv run check.py",
        []
    ]
]


def load_team_work():
    # 1. 제공 코드의 위치와 버전을 확인한다
    package = CODE / "src" / "team_work"
    if not package.is_dir():
        sys.exit(f"제공 코드를 찾지 못했습니다: {CODE}\n1.2.3항의 git clone 위치를 확인하거나 TEAM_AGENT_CODE를 지정하세요.")
    sys.path.insert(0, str(CODE / "src"))
    import team_work
    from team_work.cli import main

    if not team_work.__version__.startswith(NEEDED_VERSION):
        sys.exit(f"제공 코드 버전 {team_work.__version__}은 이 예제({NEEDED_VERSION})와 다릅니다. git -C {CODE} pull로 제공 코드를 새로 받으세요.")
    return main


def marker_done(marker):
    """끝났는지 알려 주는 표시. 'db:질의'는 기록 DB에서 1건 이상이면, 그 밖에는 파일·폴더가 있으면 끝난 것이다."""
    if marker.startswith("db:"):
        database = HERE / "state" / "requests.sqlite3"
        if not database.exists():
            return False
        import sqlite3

        with sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True) as db:
            return db.execute(marker[3:]).fetchone()[0] > 0
    return (HERE / marker).exists()


def guide():
    """지금 할 일을 보여 준다. 표시가 있으면 끝난 일로 본다(내용이 맞는지는 사람이 확인한다)."""
    print(f"예제 폴더: {HERE}\n제공 코드: {CODE}\n\n실행 순서(✓ 결과 파일이 있음):")
    progress_file = HERE / "state" / "progress.json"
    progress = json.loads(progress_file.read_text(encoding="utf-8")) if progress_file.exists() else {}
    done, notes = [], []
    for command, markers in GUIDE:
        step = command.removeprefix("uv run main.py ")
        if step in ONE_AT_A_TIME:  # 한 단계씩 진행하는 단계는 진행 위치로 판단한다
            count, total = progress.get(step, 0), len(STEPS[step][1])
            done.append(count >= total)
            notes.append(f"  ({count}/{total})")
        else:
            done.append(any(marker_done(m) for m in markers) if markers else None)
            notes.append("")
    # 다음 할 일: 아직 안 끝난 첫 단계. 그 앞에 끝났는지 알 수 없는 단계가 이어지면 그 첫 단계부터 한다
    first = next((i for i, d in enumerate(done) if d is False), None)
    if first is None:
        last = max((i for i, d in enumerate(done) if d), default=-1)
        nxt = last + 1
    else:
        nxt = first
        while nxt > 0 and done[nxt - 1] is None:
            nxt -= 1
    for i, (command, markers) in enumerate(GUIDE):
        mark = "✓" if done[i] else ("→" if i == nxt else " ")
        print(f"  {mark} {command}{notes[i]}")
    if nxt < len(GUIDE):
        print(f"\n다음: {GUIDE[nxt][0]}")
    print("\n단계:")
    for name, (desc, _) in STEPS.items():
        print(f"  {name:<10} {desc}")
    return 0


def show(path):
    target = HERE / path
    print(f"--- 확인할 내용: {path}")
    if target.suffix == ".json":
        from team_work.text import readable
        print(readable(json.loads(target.read_text(encoding="utf-8"))))
    else:
        print(target.read_text(encoding="utf-8")[:2000])
    print("---")


def run(team_work, command, extras, yes):
    # 명령 안의 {extra}는 단계 뒤에 적은 값(예: 질문 ID)으로 바꾼다
    args = []
    for part in command:
        if part == "{extra}":
            args += extras
        else:
            args.append(part.replace("{extra}", " ".join(extras)))
    if args[:2] == ["wiki", "apply-draft"] and yes:
        args.append("--yes")
    # 작업 폴더가 필요 없는 명령(평가·백업 등)은 "--no-workspace"로 시작한다
    workspace = [] if args[:1] == ["--no-workspace"] else ["--workspace", str(HERE)]
    args = args[1:] if not workspace else args
    print("$ team-work " + " ".join(args), file=sys.stderr)
    try:
        return team_work([*args, *workspace]) or 0
    except SystemExit as stop:  # 제공 코드가 오류로 멈춘 경우
        return stop.code if isinstance(stop.code, int) else 1


def describe(command):
    """기록할 내용을 명령에서 읽어 보여 준다(상태 전이·검토)."""
    def value(flag):
        return command[command.index(flag) + 1] if flag in command else "-"
    if command[:2] == ["requests", "transition"]:
        print(f"--- 기록할 상태 전이: {value('--task-id')} {value('--expected')} → {value('--status')}\n"
              f"    처리자: {value('--actor')}  이유: {value('--reason')}  근거: {value('--source-ref')}"
              + ("\n    사람 확인(완료) 표시를 함께 기록합니다." if "--human-confirmed" in command else ""))
    elif command[:2] == ["requests", "review"]:
        print(f"--- 기록할 검토: 입력 {value('--input')}  검토자 {value('--actor')}")


def confirmed(command, yes):
    """사람 확인 표시(--human-confirmed)가 들어간 명령은 사람에게 먼저 묻는다."""
    if "--human-confirmed" not in command or yes:
        return True
    try:
        return input("위 내용을 사람이 확인했고 기록해도 됩니까? [y/N] ").strip().lower() in {"y", "yes", "예", "네"}
    except (EOFError, OSError):  # 입력이 없는 자동 실행에서는 기록하지 않는다
        return False


def main():
    yes = "--yes" in sys.argv
    argv = [a for a in sys.argv[1:] if a != "--yes"]
    if not argv:
        return guide()
    step, extras = argv[0], argv[1:]
    if step not in STEPS:
        print(f"없는 단계입니다: {step}")
        return guide() or 1
    team_work = load_team_work()
    os.chdir(HERE)  # 상대 경로(input/·output/)는 이 폴더를 기준으로 읽는다
    if step != "json":
        os.environ["TEAM_WORK_TEXT"] = "1"  # 사람이 읽는 형식으로 출력(json 단계만 JSON)
    commands = STEPS[step][1]
    # 2. 한 번에 하나씩 진행하는 단계는 다음 명령 하나만 실행한다
    if step in ONE_AT_A_TIME:
        progress_file = HERE / "state" / "progress.json"
        progress = json.loads(progress_file.read_text(encoding="utf-8")) if progress_file.exists() else {}
        index = progress.get(step, 0)
        if index >= len(commands):
            print(f"{step} 단계는 {len(commands)}개를 모두 마쳤습니다. 결과: uv run main.py list")
            return 0
        if SHOW.get(step):
            show(SHOW[step][index])
        describe(commands[index])
        if not confirmed(commands[index], yes):
            print("기록하지 않았습니다. 확인한 뒤 같은 명령을 다시 실행하세요.")
            return 1
        code = run(team_work, commands[index], extras, yes)
        if code:
            print(f"\n[멈춤] {step} {index + 1}/{len(commands)}번째에서 멈췄습니다. 위 메시지를 확인하고 같은 명령을 다시 실행하세요.")
            return code
        progress[step] = index + 1
        progress_file.parent.mkdir(exist_ok=True)
        progress_file.write_text(json.dumps(progress), encoding="utf-8")
        left = len(commands) - index - 1
        print(f"\n{step} {index + 1}/{len(commands)} 완료." + (f" 다음: uv run main.py {step}" if left else " 모두 마쳤습니다."))
        return 0
    # 3. 그 밖의 단계는 명령을 차례로 실행하고, 멈추면 남은 명령을 알려 준다
    for number, command in enumerate(commands, 1):
        if SHOW.get(step):
            show(SHOW[step][number - 1])
        if "--human-confirmed" in command:
            describe(command)
        if not confirmed(command, yes):
            print("기록하지 않았습니다. 확인한 뒤 같은 명령을 다시 실행하세요.")
            return 1
        code = run(team_work, command, extras, yes)
        if code:
            if len(commands) > 1:
                print(f"\n[멈춤] {len(commands)}개 가운데 {number}번째 명령에서 멈췄습니다. 앞의 {number - 1}개는 실행됐습니다.")
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
