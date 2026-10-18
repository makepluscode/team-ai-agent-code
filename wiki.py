#!/usr/bin/env python3
"""Practice team wiki: create a copy, put raw sources in, organize, check, export.

Mirrors the book's wiki flow (3.4 ingest, 5.5 change rule and drive export,
8.4 criteria pages, 9.4 meeting records) on a local wiki folder. Standard
library only. Organizing uses Hermes (in the wiki folder, reading AGENTS.md)
or a direct commercial API call; --reference overlays the author's snapshot.

  python3 wiki.py init --wiki work/wiki --from ch03
  python3 wiki.py list
  python3 wiki.py run ch04-wiki-ingest --wiki work/wiki --outputs work/output
  python3 wiki.py check ch04-wiki-ingest --wiki work/wiki
  python3 wiki.py export --wiki work/wiki --out work/output/drive-export

Task definitions live in each chapter's tasks.json ("wiki" list); comparison
wikis in chNN/completed/studio-merry-wiki; package raw sources in chNN/wiki-raw.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "legacy"
STARTER = LEGACY / "ch02" / "wiki-starter"
TASKS = {t["id"]: t for path in sorted(LEGACY.glob("ch0*/tasks.json"))
         for t in json.loads(path.read_text(encoding="utf-8")).get("wiki", [])}
CHAPTERS = ["ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08", "ch09"]
CONFLICT = {
    "keep": "기존 페이지와 다른 내용이 있으면 덮어쓰지 말고 서로 다르다고 표시해 줘.",
    "change": "기존 페이지와 다른 내용은 규칙 파일의 변경 규칙에 따라 처리해 줘.",
}
SOURCE_MARK = "(출처: raw/"


def snapshot(chapter):
    return LEGACY / chapter / "completed" / "studio-merry-wiki"


def git(wiki, *args, check=True):
    return subprocess.run(["git", "-C", str(wiki), *args], capture_output=True, text=True, check=check)


def has_git():
    return shutil.which("git") is not None


def head(wiki):
    if not has_git() or not (Path(wiki) / ".git").exists():
        return None
    result = git(wiki, "rev-parse", "--short", "HEAD", check=False)
    return result.stdout.strip() or None


def commit(wiki, message):
    """Local practice commit. The book's wiki-sync skill does this with a remote."""
    if not has_git() or not (Path(wiki) / ".git").exists():
        return None
    git(wiki, "add", "-A")
    if not git(wiki, "status", "--porcelain").stdout.strip():
        return head(wiki)
    git(wiki, "-c", "user.name=practice", "-c", "user.email=practice@studiomerry.example",
        "commit", "-q", "-m", message)
    return head(wiki)


def overlay(source, wiki):
    for path in source.rglob("*"):
        if path.is_file():
            target = wiki / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def init(wiki, chapter="ch02"):
    wiki = Path(wiki).resolve()
    if chapter not in CHAPTERS:
        raise ValueError(f"--from은 {', '.join(CHAPTERS)} 중 하나입니다.")
    if wiki.exists() and any(wiki.iterdir()):
        raise ValueError(f"빈 위키 폴더에서 시작합니다. 기존 위키를 보존합니다: {wiki}")
    shutil.copytree(STARTER, wiki, dirs_exist_ok=True)
    if chapter != "ch02":
        overlay(snapshot(chapter), wiki)
    if has_git():
        git(wiki, "init", "-q")
        commit(wiki, f"연습 위키 시작({chapter} 끝 상태)")
    return wiki


def tree_hashes(folder):
    folder = Path(folder)
    if not folder.exists():
        return {}
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def front_matter(meta):
    lines = ["---"] + [f"{k}: {v}" for k, v in meta.items()] + ["---", ""]
    return "\n".join(lines)


def put_raws(task, wiki, outputs):
    """Place the task's raw sources. Uses the reader's own result when it exists."""
    placed = []
    for raw in task["raws"]:
        target = wiki / "raw" / raw["name"]
        if target.exists():
            placed.append({"raw": f"raw/{raw['name']}", "origin": "already-in-wiki"})
            continue
        origin = None
        if raw.get("output") and outputs and (Path(outputs) / raw["output"]).is_file():
            source, origin = Path(outputs) / raw["output"], "reader-output"
        else:
            source, origin = LEGACY / raw["fixture"], "package-fixture"
        text = source.read_text(encoding="utf-8")
        if raw.get("header"):
            meta = {**raw["header"], "made_from": origin}
            text = front_matter(meta) + text
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        placed.append({"raw": f"raw/{raw['name']}", "origin": origin})
    return placed


def add_rule_lines(task, wiki):
    """The wiki owner's rule edit (5.5 change rule, 8.4 criteria page type)."""
    lines = task.get("rule_lines") or []
    if not lines:
        return False
    rules = wiki / "AGENTS.md"
    text = rules.read_text(encoding="utf-8")
    if all(line in text for line in lines):
        return False
    anchor = "\n## 목록과 기록"
    addition = "\n".join(line for line in lines if line not in text) + "\n"
    text = text.replace(anchor, "\n" + addition + anchor, 1) if anchor in text else text + "\n" + addition
    rules.write_text(text, encoding="utf-8")
    return True


def raw_date(name):
    match = re.match(r"(\d{4})(\d{2})(\d{2})_", name)
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else datetime.now().date().isoformat()


def ingest_prompt(task, raw_name):
    template = (LEGACY / "ch03" / "prompts" / "wiki-ingest.txt").read_text(encoding="utf-8")
    return (template.replace("{{RAW}}", f"raw/{raw_name}")
            .replace("{{CONFLICT}}", CONFLICT[task.get("conflict", "keep")])
            .replace("{{EXTRA}}", task.get("instruction", "").strip())
            .replace("{{DATE}}", raw_date(raw_name)))


def wiki_files(wiki):
    files = [("AGENTS.md", wiki / "AGENTS.md")]
    files += [(p.relative_to(wiki).as_posix(), p) for p in sorted((wiki / "wiki").rglob("*.md"))]
    return files


API_FORMAT = """
# 답하는 형식
너는 파일을 직접 쓸 수 없다. 바꿀 파일의 전체 내용을 JSON 하나로만 답한다.
{"files": [{"path": "wiki/...", "content": "파일 전체 내용"}], "summary": "바뀐 파일과 변경 내용 요약"}
- path는 wiki/ 아래만 쓴다. raw/와 AGENTS.md는 바꾸지 않는다.
- 고치는 파일은 고치지 않은 부분까지 포함한 전체 내용을 다시 적는다.
- wiki/log.md는 기존 내용 전체 뒤에 한 줄을 덧붙인 전체 내용을 적는다.
"""


def apply_files(wiki, files):
    written, refused = [], []
    for item in files:
        relative = str(item.get("path", "")).lstrip("./")
        target = (wiki / relative).resolve()
        if (not relative.startswith("wiki/") or not relative.endswith(".md")
                or not target.is_relative_to((wiki / "wiki").resolve())):
            refused.append(relative)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        content = str(item.get("content", ""))
        target.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
        written.append(relative)
    return written, refused


def ingest_one(task, wiki, raw_name, engine):
    prompt = ingest_prompt(task, raw_name)
    if engine == "hermes":
        command = shutil.which("hermes")
        if not command:
            raise ValueError("헤르메스가 없습니다. --engine api 또는 --reference를 씁니다.")
        query = wiki.parent / f".ingest-{raw_name}.txt"
        query.write_text(prompt, encoding="utf-8")
        result = subprocess.run([command, "chat", "--oneshot", "--query-file", str(query)], cwd=wiki, check=False)
        query.unlink(missing_ok=True)
        if result.returncode:
            raise ValueError(f"헤르메스가 종료 코드 {result.returncode}로 끝났습니다.")
        return {"raw": raw_name, "engine": "hermes", "provider": None, "model": None, "usage": None}
    import llm
    files = wiki_files(wiki) + [(f"raw/{raw_name}", wiki / "raw" / raw_name)]
    response = llm.complete(prompt + "\n" + API_FORMAT + llm.attach(files), json_output=True, max_tokens=32768)
    call = {"raw": raw_name, "engine": "api", "provider": response["provider"], "model": response["model"],
            "usage": response["usage"], "elapsed_seconds": response["elapsed_seconds"], "attempts": response.get("attempts"),
            "http": "ok"}
    try:  # 호출은 성공했고 내용 처리에서 실패하면, 호출 기록은 남기고 실패를 알린다
        data = llm.parse_json(response["text"])
        written, refused = apply_files(wiki, data.get("files") or [])
        if refused:
            raise ValueError(f"위키 밖 또는 원본 파일을 바꾸려 했습니다: {', '.join(refused)}")
    except ValueError as error:
        error.call = {**call, "content": "failed", "error": str(error)[:200]}
        raise
    return {**call, "content": "ok", "written": written, "summary": str(data.get("summary", ""))[:400]}


def matches(wiki, pattern):
    return sorted(p for p in (wiki / "wiki").rglob("*.md")
                  if fnmatch.fnmatch(p.relative_to(wiki).as_posix(), pattern))


def check(task, wiki, before=None):
    """Return a list of problems (empty = pass). Checks structure, not prose quality."""
    wiki = Path(wiki)
    problems = []
    raws = [r["name"] for r in task["raws"]]
    for name in raws:
        if not (wiki / "raw" / name).is_file():
            problems.append(f"원본 없음: raw/{name}")
    if before is not None:
        after = tree_hashes(wiki / "raw")
        changed = [k for k, v in before["raw"].items() if after.get(k) != v]
        if changed:
            problems.append(f"원본이 바뀌었습니다: {', '.join(changed)}")
        old_log = before["log"].rstrip()
        new_log = (wiki / "wiki/log.md").read_text(encoding="utf-8")
        if not new_log.startswith(old_log):
            problems.append("log.md의 기존 기록이 바뀌었습니다(덧붙이기만 해야 함)")
    log = (wiki / "wiki/log.md").read_text(encoding="utf-8") if (wiki / "wiki/log.md").exists() else ""
    for name in raws:
        if name not in log:
            problems.append(f"log.md에 정리 기록 없음: raw/{name}")
    index = (wiki / "wiki/index.md").read_text(encoding="utf-8")
    for pattern, keywords in task["expect"].items():
        pages = matches(wiki, pattern)
        if not pages:
            problems.append(f"페이지 없음: {pattern}")
            continue
        text = "\n".join(p.read_text(encoding="utf-8") for p in pages)
        if SOURCE_MARK not in text and "raw/" not in text:
            problems.append(f"출처 표기 없음: {pattern}")
        for keyword in keywords:  # 'a|b'는 같은 뜻의 다른 표기 중 하나만 있으면 됨
            if not any(option in text for option in keyword.split("|")):
                problems.append(f"{pattern}에 '{keyword}' 없음")
        for page in pages:
            link = page.relative_to(wiki / "wiki").as_posix()
            if link not in index:
                problems.append(f"index.md에 없음: {link}")
    for name in task.get("rule_check", []):
        if name not in (wiki / "AGENTS.md").read_text(encoding="utf-8"):
            problems.append(f"규칙 파일에 '{name}' 없음")
    return problems


def run(task_id, wiki, outputs=None, engine="api", reference=False):
    task = TASKS[task_id]
    wiki = Path(wiki).resolve()
    if not (wiki / "AGENTS.md").is_file():
        raise ValueError(f"위키 폴더가 아닙니다: {wiki}. wiki.py init으로 만듭니다.")
    started = time.monotonic()
    calls = []
    if reference:
        overlay(snapshot(task["snapshot"]), wiki)
        placed = [{"raw": f"raw/{r['name']}", "origin": "author-snapshot"} for r in task["raws"]]
        problems = check(task, wiki)
    else:
        rule_changed = add_rule_lines(task, wiki)
        before = {"raw": tree_hashes(wiki / "raw"), "log": (wiki / "wiki/log.md").read_text(encoding="utf-8")}
        placed = put_raws(task, wiki, outputs)
        before["raw"] = tree_hashes(wiki / "raw")
        problems = []
        for raw in task["raws"]:
            try:
                calls.append(ingest_one(task, wiki, raw["name"], engine))
            except ValueError as error:
                if getattr(error, "call", None):
                    calls.append(error.call)
                problems.append(f"raw/{raw['name']} 정리 실패: {str(error)[:160]}")
                break
        problems = problems + check(task, wiki, before)
        if rule_changed:
            placed.append({"rule_lines_added": task["rule_lines"]})
    return {"task_id": task_id, "section": task["section"], "mode": "reference" if reference else engine,
            "placed": placed, "calls": calls, "problems": problems, "passed": not problems,
            "elapsed_seconds": round(time.monotonic() - started, 3), "wiki": str(wiki), "commit_before": head(wiki)}


# ---- 5.5 drive export (one direction, local bundle only; uploading is separate) ----

def page_meta(text):
    meta = {}
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
    return meta


def export(wiki, out, previous=None, at=None, repo="studio-merry-wiki"):
    wiki, out = Path(wiki).resolve(), Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"기존 내보내기 묶음을 보존합니다: {out}. 다른 폴더를 지정합니다.")
    exported_at = at or datetime.now().astimezone().isoformat(timespec="minutes")
    commit_id = head(wiki)
    dirty = bool(has_git() and (wiki / ".git").exists() and git(wiki, "status", "--porcelain").stdout.strip())
    index = (wiki / "wiki/index.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(((?:clients|campaigns)/[^)]+\.md)\)", index)
    if not links:
        raise ValueError("index.md에 고객·캠페인 페이지가 없습니다. 위키 정리(3.4~5.5)를 먼저 합니다.")
    rows = []
    for link in dict.fromkeys(links):
        page = wiki / "wiki" / link
        if not page.is_file():
            rows.append({"wiki_path": f"wiki/{link}", "folder": None, "status": "실패", "reason": "index.md의 페이지가 없음"})
            continue
        text = page.read_text(encoding="utf-8")
        meta = page_meta(text)
        client = meta.get("id") if meta.get("type") == "client" else meta.get("client")
        header = (f"> 이 문서는 팀 위키의 읽기 전용 사본입니다. 원본: {repo}/wiki/{link}, "
                  f"내보낸 시각: {exported_at}, 내보낸 판: {commit_id or '확인 필요'}{' (올리지 않은 변경 포함)' if dirty else ''}. "
                  "수정 요청: 위키 담당자(PM). 출처 원본(raw/)은 팀 위키에서 확인합니다.\n\n")
        for folder in ["팀 공유"] + ([f"{client} 공유"] if client in ("BB", "DP", "LB") else []):
            target = out / folder / link.replace("/", "_")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(header + text, encoding="utf-8")
            rows.append({"wiki_path": f"wiki/{link}", "folder": folder, "copy": target.relative_to(out).as_posix(),
                         "drive_file_id": None, "commit": commit_id, "exported_at": exported_at, "status": "갱신"})
    if previous:
        old = json.loads(Path(previous).read_text(encoding="utf-8"))["rows"]
        current = {(r["wiki_path"], r["folder"]) for r in rows}
        for row in old:
            if (row["wiki_path"], row["folder"]) not in current and row.get("status") != "삭제":
                rows.append({**row, "status": "삭제", "reason": "위키에서 이름이 바뀌었거나 공유 대상에서 빠짐",
                             "exported_at": exported_at})
    result = {"exported_at": exported_at, "commit": commit_id, "uncommitted_changes": dirty,
              "direction": "wiki-to-drive-only", "uploaded": False,
              "excluded": ["raw/", "guides/", "skills/", "AGENTS.md"], "rows": rows,
              "note": "로컬 사본 묶음입니다. 드라이브 업로드는 PM의 헤르메스(드라이브 MCP)가 이 목록으로 합니다. drive_file_id는 업로드 뒤 채웁니다."}
    out.mkdir(parents=True, exist_ok=True)
    (out / "export-list.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["init", "list", "run", "check", "export", "commit"])
    parser.add_argument("task", nargs="?")
    parser.add_argument("--wiki", type=Path, default=Path("work/wiki"))
    parser.add_argument("--from", dest="chapter", default="ch02")
    parser.add_argument("--outputs", type=Path, help="자신의 결과 폴더(예: work/output). 있으면 원본으로 씁니다.")
    parser.add_argument("--engine", choices=["hermes", "api"], default=None)
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--message", "-m", default="연습 위키 정리")
    args = parser.parse_args()
    try:
        if args.command == "init":
            print(f"위키 준비 완료: {init(args.wiki, args.chapter)}")
        elif args.command == "list":
            for task in TASKS.values():
                print(task["id"], task["section"], task["title"])
        elif args.command == "export":
            result = export(args.wiki, args.out or args.wiki.parent / "output/drive-export", args.previous)
            print(json.dumps({k: v for k, v in result.items() if k != "rows"} | {"rows": len(result["rows"])},
                             ensure_ascii=False, indent=2))
        elif args.command == "commit":
            print(commit(args.wiki.resolve(), args.message))
        else:
            if args.task not in TASKS:
                raise ValueError("list에서 위키 실습 ID를 고릅니다.")
            if args.command == "check":
                problems = check(TASKS[args.task], args.wiki)
                print("\n".join(problems) if problems else "통과: 원본·출처·목록·기록 구조")
                sys.exit(1 if problems else 0)
            engine = args.engine or ("hermes" if shutil.which("hermes") else "api")
            result = run(args.task, args.wiki, args.outputs, engine, args.reference)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(0 if result["passed"] else 1)
    except (ValueError, OSError) as error:
        parser.exit(1, f"확인 필요: {error}\n")


if __name__ == "__main__":
    main()
