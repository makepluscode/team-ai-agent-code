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


MAIN = '''"""{title}

입력: 이 폴더의 input/·raw/(합성 자료)
출력: 이 폴더의 state/·output/에 기록한다. 원본은 바꾸지 않는다.
실행: 이 폴더에서 `uv run main.py{usage}`
{steps_doc}
제공 코드(team_work)는 ~/team-ai-agent/code에서 찾는다. 다른 곳에 받았다면 환경 변수 TEAM_AGENT_CODE에
그 경로를 지정한다.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = Path(os.environ.get("TEAM_AGENT_CODE", Path.home() / "team-ai-agent" / "code")).expanduser()
NEEDED_VERSION = "1.7"
STEPS = {steps}
DEFAULT = {default!r}


def load_team_work():
    # 1. 제공 코드의 위치와 버전을 확인한다
    package = CODE / "src" / "team_work"
    if not package.is_dir():
        sys.exit(f"제공 코드를 찾지 못했습니다: {{CODE}}\\n1.2.3항의 git clone 위치를 확인하거나 TEAM_AGENT_CODE를 지정하세요.")
    sys.path.insert(0, str(CODE / "src"))
    import team_work
    from team_work.cli import main

    if not team_work.__version__.startswith(NEEDED_VERSION):
        sys.exit(f"제공 코드 버전 {{team_work.__version__}}은 이 예제({{NEEDED_VERSION}})와 다릅니다. git -C {{CODE}} pull 뒤 예제를 다시 복사하세요.")
    return main


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if step not in STEPS:
        sys.exit("단계를 고르세요: " + ", ".join(STEPS))
    team_work = load_team_work()
    os.chdir(HERE)  # 상대 경로(input/·output/)는 이 폴더를 기준으로 읽는다
    # 2. 고른 단계의 명령을 차례로 실행한다. 작업 폴더는 이 폴더다
    for command in STEPS[step]:
        args = [part.replace("{{extra}}", " ".join(sys.argv[2:])) for part in command]
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
'''


def write_main(folder, spec):
    steps = spec["main"]["steps"]
    doc = "\n".join(f"  {name}: {desc}" for name, (desc, _) in steps.items())
    commands = {name: cmds for name, (_, cmds) in steps.items()}
    default = spec["main"].get("default", next(iter(steps)))
    usage = " [단계]" if len(steps) > 1 else ""
    text = MAIN.format(title=spec["main"]["title"], usage=usage, steps_doc="\n단계:\n" + doc + "\n",
                       steps=json.dumps(commands, ensure_ascii=False, indent=4), default=default)
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


def main() -> int:
    failures = 0

    # 1. 제공한 원본(input/·raw/)이 그대로인지 확인한다
    sources = json.loads((HERE / ".exercise.json").read_text(encoding="utf-8"))["sources"]
    changed = [name for name, digest in sources.items()
               if not (HERE / name).is_file() or sha256(HERE / name) != digest]
    for name in changed:
        print(f"[실패] 원본이 없거나 바뀌었습니다: {{name}}")
    failures += len(changed)
    if not changed:
        print(f"[통과] 원본 {{len(sources)}}개 보존")

    # 2. 결과 파일이 실제로 저장됐는지 확인한다
    texts = []
    for name in RESULTS:
        path = HERE / name
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            print(f"[통과] 결과 파일 저장: {{name}}")
            texts.append(path.read_text(encoding="utf-8"))
        else:
            print(f"[실패] 결과 파일이 없거나 비어 있습니다: {{name}}")
            failures += 1

    # 3. 기록 DB의 건수를 확인한다
    database = HERE / "state" / "requests.sqlite3"
    for label, query, expected in COUNTS:
        if not database.exists():
            print(f"[실패] 기록 DB가 없습니다. 먼저 uv run main.py를 실행하세요: {{label}}")
            failures += 1
            continue
        with sqlite3.connect(f"{{database.as_uri()}}?mode=ro", uri=True) as db:
            actual = db.execute(query).fetchone()[0]
        mark = "통과" if actual == expected else "실패"
        failures += mark == "실패"
        print(f"[{{mark}}] {{label}}: {{actual}}건 (기준 {{expected}}건)")

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
