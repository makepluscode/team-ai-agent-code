"""4~12장 예제 폴더(code/chNN/NN-이름/)를 만든다.

입력: examples/<묶음>/chNN/start(기존 장별 시작 자료), ch02·ch03 예제 폴더(새 회의·업무 노트 자료)
출력: code/ch04~ch12의 예제 폴더. 기존 폴더는 지우고 다시 만든다.
실행: code 폴더에서 `python3 tools/make_chapter_examples.py`

시작 자료의 옛 회의 자료 이름을 2장 정리본 이름으로 바꾸고, 주간 보고(DOC-009)·입력 묶음(DOC-004)을
3장 예제와 같은 내용으로 맞춘 뒤 원본 해시 기록을 다시 계산한다. 예제별 지시문·main.py·check.py·README는
아래 SPECS에서 만든다.
"""

import hashlib
import json
import shutil
import sys
import textwrap
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
EXAMPLES = CODE / "examples"
CH03 = CODE / "ch03" / "02-weekly-report"
NEW_NOTES = CH03 / "input" / "organized"
NEW_DOC004 = CH03 / "input" / "DOC-004_weekly-meetings.md"
NEW_DOC009 = CH03 / "expected" / "DOC-009_weekly-report.r1.md"

# 2장 개편 전 정리본 이름 → 개편 뒤 이름
RENAMES = {
    "2026-10-02_주간회의_안내준비점검.md": "2026-10-02_회의노트_주간회의.md",
    "2026-10-05_주간회의_온보딩준비.md": "2026-10-05_회의노트_주간회의.md",
    "2026-10-06_원온원_자료접근점검.txt": "2026-10-06_회의노트_원온원.txt",
    "2026-10-06_업무메모_비교표작성.md": "2026-10-06_업무노트_비교표작성.md",
    "2026-10-07_상태메모_준비업무점검.txt": "2026-10-07_업무노트_준비상태점검.txt",
    "주간 보고 입력 묶음(회의 자료 정리본)": "주간 보고 입력 묶음(회의 노트·업무 노트 정리본)",
    "텍스트 회의 자료 6개": "텍스트 노트 8개",
}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".csv"}
DROP = {"my-instructions.md", "jobs.json", "weekly-activity.csv", ".keep"}
SHARED = CODE / "tools" / "example_templates"
# 예제 폴더를 만들 위치. 테스트는 --out으로 임시 폴더를 넘겨 저장소를 건드리지 않는다
OUT = CODE


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob("*")) if p.is_file()}


def doc009_r2(r1):
    """3장 주간 보고(r1)에서 9장 검토로 확정한 r2를 만든다(누락 확인·검토 기록 추가)."""
    head, body = r1.split("---\n", 2)[1:]
    head = (head.replace('revision: "r1"', 'revision: "r2"')
            .replace('created_at: "2026-10-07T09:00:00+09:00"', 'created_at: "2026-10-14T15:02:00+09:00"')
            .replace('effective_at: "2026-10-07T09:00:00+09:00"', 'effective_at: "2026-10-14T15:02:00+09:00"')
            .replace('state: "초안"', 'state: "확정"')
            .replace('source_refs: ["DOC-004@r1"]', 'source_refs: ["DOC-004@r1", "DOC-009@r1"]\nsupersedes: "DOC-009@r1"'))
    body = body.replace("업무 TASK-001 상태: 확인 대기.", "업무 TASK-001 상태: 완료.")
    body = body.replace("\n출처:", "\n누락값은 여전히 확인되지 않아 미입력으로 보존합니다. M03이 10/14 15:00 누락 확인을 수행했고 "
                        "M01이 15:02 검토했습니다. TASK-001은 보고 검토 완료로 처리합니다. 입력 기간 전체의 활동 완료를 "
                        "뜻하지 않습니다.\n\n출처:", 1)
    body = body.rstrip() + ("\n\n## summary\n\n관측 완료4건(ITEM-001~004) 유지. ITEM-006 상태 미기재, 10/08~09 미입력 보존. "
                            "REV-002-input의 미입력0 오류를 복구했습니다. 원본r1 보존, 누락 확인 M03·검토 M01, 수정 이력 REV-002.\n")
    return f"---\n{head}---\n{body}"


def migrate(folder):
    """옛 회의 자료 이름과 주간 보고를 2·3장 새 자료로 맞추고 해시 기록을 다시 계산한다."""
    # 1. 쓰지 않는 옛 설정 파일을 뺀다
    for path in list(folder.rglob("*")):
        if path.is_file() and path.name in DROP:
            path.unlink()
    # 2. 정리본 폴더는 3장 예제의 텍스트 노트 8개로 바꾼다(사진·확인 필요 파일 제외)
    for organized in [p for p in folder.rglob("organized") if p.is_dir()]:
        shutil.rmtree(organized)
        shutil.copytree(NEW_NOTES, organized)
    # 3. 입력 묶음과 주간 보고는 3장 예제와 같은 내용으로 바꾼다
    for path in folder.rglob("*"):
        if path.name in {"DOC-004_weekly-meetings.md", "DOC-004_r1.md"}:
            path.write_bytes(NEW_DOC004.read_bytes())
        elif path.name in {"DOC-009_weekly-report.r1.md", "DOC-009_r1.md"}:
            path.write_bytes(NEW_DOC009.read_bytes())
        elif path.name == "DOC-009_r2.md":
            path.write_text(doc009_r2(NEW_DOC009.read_text(encoding="utf-8")), encoding="utf-8")
    # 4. 나머지 텍스트의 옛 이름을 새 이름으로 바꾼다
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix in TEXT_SUFFIXES and path.parent.name != "organized":
            text = path.read_text(encoding="utf-8")
            new = text
            for old, renamed in RENAMES.items():
                new = new.replace(old, renamed)
            if new != text:
                path.write_text(new, encoding="utf-8")
    # 5. 원본 등록 기록(JSON)의 해시를 다시 계산하고 없는 파일 항목은 뺀다
    for path in folder.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list) and data and all(isinstance(x, dict) and "sha256" in x for x in data):
            data = fix_registry(folder, data)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fix_registry(folder, items):
    keep, seen = [], set()
    key = next((k for k in ("preserved_path", "registered_path") if k in items[0]), None)
    for item in items:
        target = folder / item.get(key, "") if key else None
        if key and not target.is_file():
            continue
        if target:
            item["sha256"] = sha(target)
        keep.append(item)
        seen.add(item.get(key))
    # 정리본 폴더에 새로 생긴 노트(할 일·통화 메모)도 같은 형식으로 등록한다
    if key:
        organized = sorted({Path(i[key]).parent.as_posix() for i in keep if "/organized/" in i.get(key, "") + "/"})
        sample = next((i for i in keep if "/organized/" in i.get(key, "")), None)
        for parent in organized:
            for note in sorted((folder / parent).glob("*")):
                relative = f"{parent}/{note.name}"
                if relative not in seen and sample:
                    item = dict(sample)
                    for k, v in sample.items():
                        if isinstance(v, str) and sample[key].rsplit("/", 1)[1] in v:
                            item[k] = v.replace(sample[key].rsplit("/", 1)[1], note.name)
                    item[key], item["sha256"] = relative, sha(note)
                    keep.append(item)
    return keep


EDITABLE = ["input/routing-criteria.json"]


def write_metadata(folder, chapter):
    # 독자가 고쳐 쓰는 설정 파일은 원본 해시 검사에서 뺀다
    editable = [k for k in EDITABLE if (folder / k).is_file()]
    sources = {k: v for k, v in hashes(folder).items() if k.startswith(("input/", "raw/")) and k not in editable}
    meta = {"chapter": chapter, "package_version": "1.7", "sources": sources, "data_kind": "synthetic",
            "reference_kind": "edited-reference", "editable_settings": editable,
            "example": folder.relative_to(OUT).as_posix()}
    if (folder / "wiki").is_dir():
        meta["wiki_base"] = hashes(folder / "wiki")
    (folder / ".exercise.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dedent(text):
    return textwrap.dedent(text).strip() + "\n"


def build(spec):
    chapter, name = spec["chapter"], spec["name"]
    folder = OUT / f"ch{chapter:02}" / name
    if folder.exists():
        shutil.rmtree(folder)
    base = spec.get("base")
    if base:
        shutil.copytree(EXAMPLES / base / "start", folder)
    else:
        folder.mkdir(parents=True)
    migrate(folder)
    for relative in spec.get("remove", []):
        target = folder / relative
        shutil.rmtree(target) if target.is_dir() else target.unlink(missing_ok=True)
    for relative, source in spec.get("copy", {}).items():
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        src = CODE / source
        if src.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target)
            migrate(target) if spec.get("migrate_copies", True) else None
        else:
            shutil.copy(src, target)
    for pattern, keys in spec.get("json_drop", {}).items():
        for target in sorted(folder.glob(pattern)):
            data = json.loads(target.read_text(encoding="utf-8"))
            for key in keys:
                data.pop(key, None)
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for relative, pairs in spec.get("rewrite", {}).items():
        target = folder / relative
        text = target.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        target.write_text(text, encoding="utf-8")
    for relative, text in spec.get("files", {}).items():
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dedent(text), encoding="utf-8")
    write_metadata(folder, chapter)
    # 메타데이터를 만든 뒤에 쓰는 파일(지시문·스크립트·안내)은 원본 해시에 넣지 않는다
    for relative, text in spec.get("after", {}).items():
        target = folder / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dedent(text), encoding="utf-8")
    if "main" in spec:
        write_main(folder, spec)
    write_check(folder, spec)
    write_pyproject(folder, spec)
    write_readme(folder, spec)
    return folder


MAIN = r'''"""__TITLE__

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서
  uv run main.py            지금 할 일과 단계 목록(아무것도 실행하지 않음)
  uv run main.py <단계>     단계 실행. 사람 확인이 필요한 단계는 내용을 보여 주고 y/N을 묻는다
  uv run main.py <단계> --yes   확인 질문만 생략(충돌·원본 검사는 그대로)
__STEPS_DOC__
제공 코드(team_work)는 ~/team-ai-agent/code에서 찾는다. 다른 곳에 받았다면 환경 변수 TEAM_AGENT_CODE에
그 경로를 지정한다. 단계의 실제 처리는 code/src/team_work/에 있고, 이 파일은 단계 이름과 명령을 잇기만 한다.
"""

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = Path(os.environ.get("TEAM_AGENT_CODE", Path.home() / "team-ai-agent" / "code")).expanduser()
NEEDED_VERSION = "1.7"
# 단계 이름 → 설명과 team-work 명령 목록
STEPS = __STEPS__
# 한 번 실행할 때 명령 하나씩 진행하는 단계(진행 위치는 state/progress.json)
ONE_AT_A_TIME = __ONE__
# 명령을 실행하기 전에 보여 줄 파일(사람이 확인할 내용)
SHOW = __SHOW__
# 책의 실행 순서와, 끝났는지 알 수 있는 파일(없으면 빈 목록)
GUIDE = __GUIDE__


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
'''


def guide_from(spec):
    """README의 실행 순서에서 cp·cd를 빼고, 끝났는지 알 수 있는 파일을 붙인다."""
    markers = spec["main"].get("markers", {})
    results = [r for r in spec.get("check", {}).get("results", []) if r.startswith("output/") and "wiki-base" not in r]
    guide = []
    for command in spec["readme"]["run"]:
        if command.startswith(("cp ", "cd ", "mkdir -p ~/agent-work")):
            continue
        if command in markers:
            found = markers[command]
        elif command == "hermes chat --query-file prompt.md":
            wiki = any(c[:2] == ["wiki", "apply-draft"] for _, cmds in spec["main"]["steps"].values() for c in cmds)
            found = ["output/wiki-draft", "output/wiki-draft-applied"] if wiki else results[:1]
        elif command == "uv run main.py setup" and spec["chapter"] >= 7:
            found = ["state/requests.sqlite3"]
        elif command == "uv run main.py intake":
            found = ["db:SELECT COUNT(*) FROM requests"]
        elif command == "uv run main.py apply":
            found = ["output/wiki-base.json"]
        elif command == "uv run main.py register":
            source = next(c[c.index("--source") + 1] for _, cmds in spec["main"]["steps"].values() for c in cmds
                          if "--source" in c and c[:2] == ["wiki", "register"])
            found = ["raw/" + Path(source).name]
        else:
            found = []
        guide.append([command, found])
    return guide


def write_main(folder, spec):
    steps = spec["main"]["steps"]
    doc = "\n".join(f"  {name}: {desc}" for name, (desc, _) in steps.items())
    text = (MAIN.replace("__TITLE__", spec["main"]["title"])
            .replace("__STEPS_DOC__", "\n단계:\n" + doc + "\n")
            .replace("__STEPS__", json.dumps({n: [d, c] for n, (d, c) in steps.items()}, ensure_ascii=False, indent=4))
            .replace("__ONE__", json.dumps(spec["main"].get("one_at_a_time", []), ensure_ascii=False))
            .replace("__SHOW__", json.dumps(spec["main"].get("show", {}), ensure_ascii=False, indent=4))
            .replace("__GUIDE__", json.dumps(guide_from(spec), ensure_ascii=False, indent=4)))
    (folder / "main.py").write_text(text, encoding="utf-8")


CHECK = '''"""{title}

입력: .exercise.json(이 예제가 제공한 원본의 기준 해시){inputs}
출력: 화면에 자동 확인 결과와 사람이 직접 확인할 항목을 출력한다. 파일은 바꾸지 않는다.
실행: 이 폴더에서 `uv run check.py`
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 있어야 하는 결과 파일(이 폴더 기준)
RESULTS = {results}
# SQLite 기록 확인: (설명, 질의, 기대 개수)
COUNTS = {counts}
# 사람이 대조할 질문과, 그 자리를 찾기 쉽게 보여 줄 표현
HUMAN_CHECKS = {human}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hint(name: str) -> str:
    """빠진 결과 파일마다 다음에 할 일을 알려 준다."""
    if name == "output/wiki-base.json":
        return "변경안을 uv run main.py preview로 확인한 뒤 uv run main.py apply로 적용하세요."
    if name.startswith("raw/"):
        return "uv run main.py register로 원본을 등록하세요."
    if name.startswith("wiki/"):
        return "헤르메스 변경안(output/wiki-draft/)을 확인하고 적용했는지 보세요(uv run main.py로 할 일 확인)."
    if name.startswith("../"):
        return "uv run main.py backup과 uv run main.py restore를 실행했는지 보세요."
    return "헤르메스 지시문을 실행해 이 이름으로 저장했는지 보세요. 다른 이름으로 저장됐다면 지시문의 저장 경로를 확인합니다."


def main() -> int:
    failures = 0

    # 1. 제공한 원본(input/·raw/)이 그대로인지 확인한다
    sources = json.loads((HERE / ".exercise.json").read_text(encoding="utf-8"))["sources"]
    changed = [name for name, digest in sources.items()
               if not (HERE / name).is_file() or sha256(HERE / name) != digest]
    for name in changed:
        print(f"[실패] 원본이 없거나 바뀌었습니다: {{name}}")
    if changed:
        print("    → 원본은 고치지 않습니다. 장 폴더를 새 이름으로 다시 복사해 시작하세요.")
    failures += len(changed)
    if not changed:
        print(f"[통과] 원본 {{len(sources)}}개 보존")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    texts = []
    for name in RESULTS:
        path = HERE / name
        try:
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
        except UnicodeDecodeError:  # DB 같은 이진 파일은 비어 있지 않은지만 본다
            text = "" if not path.stat().st_size else None
        if text is None or text.strip():
            print(f"[통과] 결과 파일 저장: {{name}}")
            texts.append(text or "")
        else:
            print(f"[실패] 결과 파일이 없거나 비어 있습니다: {{name}}")
            print(f"    → {{hint(name)}}")
            failures += 1

    # 3. 기록 DB의 건수를 확인한다
    database = HERE / "state" / "requests.sqlite3"
    for label, query, expected in COUNTS:
        if not database.exists():
            print(f"[실패] 기록 DB가 없습니다: {{label}}")
            print("    → uv run main.py로 할 일을 보고 setup(또는 intake) 단계를 먼저 실행하세요.")
            failures += 1
            continue
        with sqlite3.connect(f"{{database.as_uri()}}?mode=ro", uri=True) as db:
            actual = db.execute(query).fetchone()[0]
        mark = "통과" if actual == expected else "실패"
        failures += mark == "실패"
        print(f"[{{mark}}] {{label}}: {{actual}}건 (기준 {{expected}}건)")
        if mark == "실패":
            print("    → uv run main.py로 아직 실행하지 않은 단계를 확인하세요. 결과를 보려면 uv run main.py list")

    # 4. 사람이 대조할 자리를 보여 준다. 표현이 있다고 내용이 맞다는 뜻은 아니다
    if HUMAN_CHECKS:
        print("\\n사람이 확인할 항목(원본·expected/와 대조):")
        text = "\\n".join(texts)
        for question, words in HUMAN_CHECKS:
            print(f"- {{question}}")
            lines = [line.strip() for line in text.splitlines() if any(w in line for w in words)]
            for line in lines[:3]:
                print(f"    {{line[:120]}}")

    print("\\n자동 확인:", "통과" if failures == 0 else f"실패 {{failures}}건")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
'''


def write_check(folder, spec):
    check = spec.get("check", {})
    results = check.get("results", [])
    inputs = ("\n결과: " + ", ".join(results)) if results else ""
    text = CHECK.format(title=check.get("title", f"{spec['title']} 예제의 결과를 확인한다."), inputs=inputs,
                        results=json.dumps(results, ensure_ascii=False),
                        counts=json.dumps(check.get("counts", []), ensure_ascii=False),
                        human=json.dumps(check.get("human", []), ensure_ascii=False))
    (folder / "check.py").write_text(text, encoding="utf-8")


def write_pyproject(folder, spec):
    deps = spec.get("deps", [])
    lines = ",\n".join(f'    "{d}"' for d in deps)
    body = f"[\n{lines},\n]" if deps else "[]"
    optional = "".join(f'\n[project.optional-dependencies]\n{name} = [{", ".join(chr(34) + d + chr(34) for d in items)}]\n'
                       for name, items in spec.get("optional_deps", {}).items())
    (folder / "pyproject.toml").write_text(
        f'[project]\nname = "ch{spec["chapter"]:02}-{spec["name"]}"\nversion = "0.1.0"\n'
        f'description = "{spec["chapter"]}장 {spec["title"]} 예제"\nrequires-python = ">=3.11"\n'
        f"dependencies = {body}\n{optional}", encoding="utf-8")


def write_readme(folder, spec):
    rows = "\n".join(f"| {name} | {role} |" for name, role in spec["readme"]["files"])
    run = "\n".join(spec["readme"]["run"])
    notes = ("\n\n" + dedent(spec["readme"]["notes"])) if spec["readme"].get("notes") else "\n"
    text = (f"# {spec['name']}: {spec['title']}\n\n{dedent(spec['readme']['intro'])}\n## 실행 방법\n\n"
            f"```bash\n{run}\n```\n\n## 폴더 구성\n\n| 파일 | 역할 |\n|---|---|\n{rows}\n{notes}")
    (folder / "README.md").write_text(text.rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    from chapter_example_specs import SPECS

    if sys.argv[1:2] == ["--out"]:
        OUT = Path(sys.argv[2]).resolve()
    for spec in SPECS:
        print("built", build(spec).relative_to(OUT))
