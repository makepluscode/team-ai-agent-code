"""Explicit wiki registration, proposed edits and confirmation; reuse sync skill."""

import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import models
from .io import read_text, write_json, write_new
from .workspace import PACKAGE_ROOT, hashes, verify


def register(workspace, source):
    if Path(source).is_symlink():
        raise ValueError("심볼릭 링크 원본은 등록하지 않습니다.")
    work, source = Path(workspace).resolve(), Path(source).resolve()
    verify(work)
    if not (work / "wiki").is_dir():
        raise ValueError("4장 이후 위키 작업 폴더가 필요합니다.")
    if not source.is_file() or source.is_symlink():
        raise ValueError("원본 파일을 확인하세요.")
    target = work / "raw" / source.name
    if target.exists():
        raise ValueError("동일 이름의 원본을 보존합니다. 새 버전 이름을 쓰세요.")
    marker = work / "output" / f"{source.name}.registration.json"
    if marker.exists() or not target.resolve().is_relative_to(work / "raw"):
        raise ValueError("기존 등록 기록이나 원본 경로를 확인하세요.")
    text = read_text(source)
    # Use the same source hashing convention as legacy wiki.py, without its auto-commit.
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    write_new(target, text)
    write_json(
        marker,
        {
            "original_path": str(source),
            "registered_path": f"raw/{source.name}",
            "sha256": sha,
            "actor_id": "wiki-curator",
            "data_kind": "actual-file-registration",
        },
    )
    metadata = json.loads(read_text(work / ".exercise.json"))
    metadata["sources"][f"raw/{source.name}"] = sha
    (work / ".exercise.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"registered": str(target), "sha256": sha}


def _suffix(number):
    return "" if number == 1 else f"-{number}"


def propose(workspace):
    work = Path(workspace).resolve()
    verify(work)
    # Earlier proposals and run logs stay as records; a repeat gets the next number.
    number = 1
    while any((work / f"output/wiki-proposal{_suffix(number)}{ext}").exists() for ext in (".json", ".run.json")):
        number += 1
    proposal = work / f"output/wiki-proposal{_suffix(number)}.json"
    log = work / f"output/wiki-proposal{_suffix(number)}.run.json"
    before = hashes(work / "wiki")
    attachments = [("AGENTS.md", work / "AGENTS.md")]
    attachments += [
        (p.relative_to(work).as_posix(), p)
        for folder in ("raw", "wiki")
        for p in sorted((work / folder).rglob("*"))
        if p.is_file() and p.suffix in {".md", ".txt", ".json"}
    ]
    llm = models.legacy_module("llm")
    legacy = models.legacy_module("wiki")
    record = {
        "data_kind": "observed",
        "artifact_kind": "execution-log",
        "status": "failed",
        "run_id": "RUN-OBS-" + uuid.uuid4().hex,
        "actor_id": "wiki-curator",
        "usage": None,
    }
    try:
        response = models.call_commercial(
            "wiki-curator 한 곳이 위키를 정리합니다. 원본·과거 버전은 보존하고 현재 결정·취소·미정을 구별합니다.",
            read_text(work / "prompts/wiki.txt") + legacy.API_FORMAT + llm.attach(attachments),
            json_output=True,
        )
        record.update(
            {k: response.get(k) for k in ("provider", "model", "usage", "elapsed_seconds")}
        )
        verify(work)
        if hashes(work / "wiki") != before:
            raise ValueError("제안 중 위키가 바뀌었습니다. 충돌로 중단합니다.")
        data = models.parse_json(response["text"])
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("files"), list)
            or not data["files"]
        ):
            raise ValueError("제안 파일 목록이 없습니다. 위키는 바뀌지 않았습니다.")
        seen = set()
        for item in data["files"]:
            if not isinstance(item, dict):
                raise ValueError("잘못된 위키 제안 항목입니다.")  # noqa: TRY004
            relative = item.get("path", "")
            path = (work / relative).resolve()
            if (
                not relative.startswith("wiki/")
                or not relative.endswith(".md")
                or not path.is_relative_to(work / "wiki")
                or relative in seen
                or not isinstance(item.get("content"), str)
            ):
                raise ValueError("위키 밖 경로·중복·잘못된 내용으로 중단합니다.")
            seen.add(relative)
            item["before_sha256"] = before.get(path.relative_to(work / "wiki").as_posix())
        data.update(
            {
                "data_kind": "observed",
                "artifact_kind": "actual-model-proposal",
                "actor_id": "wiki-curator",
                "provider": response["provider"],
                "model": response["model"],
                "usage": response["usage"],
            }
        )
        write_json(proposal, data)
        record["status"] = "proposed-awaiting-confirmation"
    except Exception:
        record["error_kind"] = "proposal-or-validation-failed"
        write_json(log, record)
        raise
    write_json(log, record)
    return {"proposal": proposal.relative_to(work).as_posix(), "applied": False}


def apply(workspace, proposal, confirmed=False):
    if not confirmed:
        raise ValueError("파일 제안과 출처를 읽고 --confirm으로 적용하세요.")
    work = Path(workspace).resolve()
    verify(work)
    data = json.loads(read_text(proposal))
    if not isinstance(data.get("files"), list) or not data["files"]:
        raise ValueError("빈 제안입니다.")
    stem = Path(proposal).stem
    suffix = stem.removeprefix("wiki-proposal") if stem.startswith("wiki-proposal-") else ""
    marker = work / f"output/wiki-applied{suffix}.json"
    if marker.exists():
        raise ValueError("이미 적용한 제안입니다.")
    plans, seen = [], set()
    for item in data["files"]:
        relative = item.get("path", "")
        target = (work / relative).resolve()
        if (
            not relative.startswith("wiki/")
            or not relative.endswith(".md")
            or not target.is_relative_to(work / "wiki")
            or relative in seen
            or not isinstance(item.get("content"), str)
        ):
            raise ValueError("잘못된 제안 경로·내용입니다. 아무 파일도 적용하지 않았습니다.")
        seen.add(relative)
        sha = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
        if "before_sha256" not in item or sha != item["before_sha256"]:
            raise ValueError(f"제안 뒤 파일이 바뀌었습니다. 충돌로 중단합니다: {relative}")
        plans.append((target, item["content"]))
    backup = work / f"output/wiki-before{suffix}"
    if backup.exists():
        raise ValueError("기존 복구 자료를 보존합니다.")
    shutil.copytree(work / "wiki", backup)
    log = work / "wiki/log.md"
    try:
        for target, content in plans:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content + ("" if content.endswith("\n") else "\n"), encoding="utf-8")
        # The curation record must not depend on whether the model proposed log.md.
        entry = (
            f"- {datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')} · wiki-curator · 사람 확인 후 적용 · "
            + ", ".join(t.relative_to(work).as_posix() for t, _ in plans)
            + f" · 제안 {Path(proposal).name}\n"
        )
        text = log.read_text(encoding="utf-8") if log.exists() else "# 정리 기록\n\n"
        log.write_text(text + ("" if text.endswith("\n") else "\n") + entry, encoding="utf-8")
    except OSError:
        for target, _ in plans + [(log, None)]:
            old = backup / target.relative_to(work / "wiki")
            if old.exists():
                shutil.copy2(old, target)
            elif target.exists():
                target.unlink()
        raise ValueError(
            "적용 중 IO 오류로 이전 위키 파일을 복구했습니다. 백업을 확인하세요."
        ) from None
    write_json(
        marker,
        {
            "actor_id": "wiki-curator",
            "confirmed": True,
            "source": str(proposal),
            "backup": backup.relative_to(work).as_posix(),
        },
    )
    return {"applied": len(plans), "backup": str(backup)}


def _wiki_base(work):
    """마지막으로 적용한 위키 상태의 해시. 처음에는 예제 폴더에 기록된 시작 상태를 쓴다."""
    base = work / "output" / "wiki-base.json"
    if base.exists():
        return json.loads(read_text(base))
    return json.loads(read_text(work / ".exercise.json")).get("wiki_base", {})


def _read_draft(work, draft):
    """변경안 폴더를 읽어 (폴더, 기준 해시, 파일 목록)을 돌려준다. 위키가 마지막 적용 뒤 바뀌었으면 멈춘다."""
    folder = (work / draft).resolve()
    if not folder.is_dir() or not folder.is_relative_to(work / "output"):
        raise ValueError(f"변경안 폴더가 없습니다: {draft}. 헤르메스 지시문(prompt.md)을 실행해 변경안을 저장했는지 확인하세요.")
    # 1. 위키가 마지막 적용 상태 그대로인지 확인한다(직접 고친 흔적이 있으면 멈춘다)
    base = _wiki_base(work)
    current = hashes(work / "wiki")
    if current != base:
        changed = sorted(k for k in set(base) | set(current) if base.get(k) != current.get(k))
        raise ValueError("마지막 적용 뒤 wiki/가 바뀌었습니다. 충돌로 중단합니다. 바뀐 파일: " + ", ".join(changed)
                         + ". 직접 고친 내용은 예제 폴더 밖에 따로 적어 두고, uv run reset.py로 처음 상태로 되돌린 뒤 그 내용을 지시문에 넣어 다시 하세요.")
    # 2. 변경안을 기존 apply가 읽는 제안 파일 형식으로 옮긴다
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("변경안에 심볼릭 링크가 있습니다.")
        if path.is_file():
            relative = path.relative_to(folder).as_posix()
            files.append({"path": f"wiki/{relative}", "content": read_text(path),
                          "before_sha256": base.get(relative)})
    if not files:
        raise ValueError("변경안 폴더가 비어 있습니다.")
    return folder, files


def preview_draft(workspace, draft="output/wiki-draft"):
    """변경안이 위키에 적용되면 바뀔 줄을 diff로 돌려준다. 파일은 바꾸지 않는다."""
    work = Path(workspace).resolve()
    verify(work)
    _, files = _read_draft(work, draft)
    parts = []
    for item in files:
        target = work / item["path"]
        old = read_text(target).splitlines(keepends=True) if target.exists() else []
        new = item["content"].splitlines(keepends=True)
        label = "새 파일" if not target.exists() else "수정"
        diff = "".join(difflib.unified_diff(old, new, f"현재 {item['path']}", f"변경안 {item['path']}"))
        parts.append(f"=== {label}: {item['path']}\n" + (diff or "(바뀌는 줄 없음)\n"))
    parts.append("=== 자동 추가: wiki/log.md에 적용 시각·wiki-curator·적용 파일 목록 한 줄\n")
    return "".join(parts)


def apply_draft(workspace, draft="output/wiki-draft", confirmed=False):
    """헤르메스가 output/wiki-draft/에 쓴 변경안을 사람이 확인한 뒤 위키에 적용한다.

    변경안 폴더의 상대 경로가 wiki/ 아래 경로가 된다(예: wiki-draft/guides/onboarding.md).
    confirmed가 아니면 적용하지 않는다(CLI는 diff를 보여 준 뒤 y로 확인받는다).
    위키가 마지막 적용 뒤에 바뀌었으면 충돌로 멈추고, 적용 전 위키는 output/wiki-before-N에 남긴다.
    """
    if not confirmed:
        raise ValueError("변경안을 확인한 뒤 적용하세요(uv run main.py preview로 diff 확인).")
    work = Path(workspace).resolve()
    verify(work)
    folder, files = _read_draft(work, draft)
    number = 1
    while (work / f"output/wiki-proposal{_suffix(number)}.json").exists():
        number += 1
    proposal = work / f"output/wiki-proposal{_suffix(number)}.json"
    write_json(proposal, {"files": files, "actor_id": "wiki-curator", "artifact_kind": "hermes-draft",
                          "draft": folder.relative_to(work).as_posix()})
    # 3. 충돌 검사·백업·정리 기록을 맡는 기존 apply로 적용하고, 새 기준 상태를 남긴다
    result = apply(work, proposal, confirmed=True)
    # 기준 상태는 적용할 때마다 덮어쓴다(write_json은 새 파일 전용이라 두 번째 적용에서 멈춘다)
    (work / "output" / "wiki-base.json").write_text(
        json.dumps(hashes(work / "wiki"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    kept = work / f"output/wiki-draft-applied{_suffix(number)}"
    folder.rename(kept)
    return {**result, "proposal": proposal.relative_to(work).as_posix(),
            "files": [item["path"] for item in files], "draft_kept": kept.relative_to(work).as_posix(),
            "next": "적용한 변경안은 위의 보관 폴더로 옮겼습니다. 다시 바꾸려면 헤르메스에 새 변경안을 output/wiki-draft/에 쓰게 한 뒤 preview부터 합니다. 결과 확인: uv run check.py"}


def receive(workspace, source):
    """다른 작업 폴더(담당자)의 위키를 이 폴더(동료)로 받아 온다. 원본(raw/)이 같을 때만 받는다.

    받기 전 위키는 output/wiki-before-receive-N에 남기고, 받은 위키를 다음 적용의 기준 상태로 삼는다.
    """
    work, other = Path(workspace).resolve(), Path(source).expanduser().resolve()
    verify(work)
    if not (other / "wiki").is_dir() or other == work:
        raise ValueError(f"받을 위키가 없습니다: {other}/wiki. 담당 폴더 경로를 확인하세요.")
    # 1. 같은 이름의 원본이 두 폴더에서 같은지 확인한다(다르면 서로 다른 자료로 정리한 위키다)
    mine, theirs = hashes(work / "raw"), hashes(other / "raw")
    differ = sorted(k for k in set(mine) & set(theirs) if mine[k] != theirs[k])
    if differ:
        raise ValueError("두 폴더의 같은 이름 원본이 다릅니다: " + ", ".join(differ))
    only = sorted(set(theirs) ^ set(mine))
    if only:
        raise ValueError("한쪽 폴더에만 있는 원본이 있습니다: " + ", ".join(only)
                         + ". 담당 폴더에서 원본 등록(uv run main.py register)과 위키 적용을 마쳤는지 확인하세요.")
    # 2. 담당 폴더가 변경안을 적용한 뒤 위키를 그대로 두었는지 확인한다(적용 전 위키나 직접 고친 위키는 받지 않는다)
    base = other / "output" / "wiki-base.json"
    if not base.is_file() or json.loads(read_text(base)) != hashes(other / "wiki"):
        raise ValueError("담당 폴더의 위키가 적용을 마친 상태가 아닙니다. 담당 폴더에서 uv run main.py preview와 "
                         "uv run main.py apply를 마친 뒤 받으세요.")
    # 3. 받을 위키를 임시 폴더에 먼저 복사하고, 받기 전 위키를 보관한 뒤 바꾼다(복사가 실패하면 지금 위키는 그대로다)
    number = 1
    while (work / f"output/wiki-before-receive{_suffix(number)}").exists():
        number += 1
    backup = work / f"output/wiki-before-receive{_suffix(number)}"
    incoming = work / "output" / ".wiki-receiving"
    if incoming.exists():
        shutil.rmtree(incoming)
    shutil.copytree(other / "wiki", incoming, symlinks=False)
    shutil.copytree(work / "wiki", backup)
    try:
        shutil.rmtree(work / "wiki")
        incoming.rename(work / "wiki")
    except OSError:
        if (work / "wiki").exists():
            shutil.rmtree(work / "wiki")
        shutil.copytree(backup, work / "wiki")
        raise ValueError(f"위키를 바꾸지 못해 받기 전 위키로 되돌렸습니다. 보관본: {backup.relative_to(work)}") from None
    with (work / "wiki" / "log.md").open("a", encoding="utf-8") as log:
        stamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
        log.write(f"- {stamp} · 위키 받기 · {other.name}에서 받음(받기 전 위키: {backup.relative_to(work).as_posix()})\n")
    # 4. 받은 위키를 다음 변경안 적용의 기준 상태로 삼는다
    (work / "output" / "wiki-base.json").write_text(
        json.dumps(hashes(work / "wiki"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"received_from": str(other), "backup": backup.relative_to(work).as_posix(),
            "files": sorted(hashes(work / "wiki"))}


def search(workspace, query):
    work = Path(workspace).resolve()
    verify(work)
    return [
        {"source": p.relative_to(work).as_posix(), "line": i, "text": line}
        for p in sorted((work / "wiki").rglob("*.md"))
        for i, line in enumerate(read_text(p).splitlines(), 1)
        if any(term in line for term in query.split())
    ]


def sync(workspace, arguments):
    work = Path(workspace).resolve()
    script = work / "skills/wiki-sync/scripts/wiki_sync.py"
    if not script.is_file():
        script = PACKAGE_ROOT / "legacy/ch02/wiki-starter/skills/wiki-sync/scripts/wiki_sync.py"
    # The reused skill handles selected files, rejects force and stops on conflict.
    return subprocess.run(
        [sys.executable, str(script), *arguments], cwd=work, check=False
    ).returncode
