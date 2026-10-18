"""One personal reminder, explicit run, pause and portable backup."""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .io import read_text, write_json
from .workspace import hashes, verify


def schedule(workspace, action, at=None, confirmed=False):
    work = Path(workspace).resolve()
    verify(work)
    path = work / "output/personal-schedule.json"
    if action == "create":
        if not at:
            raise ValueError("--at에 +09:00 시각을 명시하세요.")
        due = datetime.fromisoformat(at)
        if due.utcoffset() is None:
            raise ValueError("시간대가 필요합니다.")
        write_json(
            path,
            {
                "scope": "personal",
                "task": "weekly-report",
                "due_at": due.isoformat(),
                "state": "active",
                "run_count": 0,
                "registration_kind": "provided-runner",
                "hermes_registered": False,
            },
        )
    elif action == "status":
        return json.loads(read_text(path))
    elif action == "pause":
        data = json.loads(read_text(path))
        data["state"] = "paused"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif action == "run-due":
        if not confirmed:
            raise ValueError("실제 상용 호출을 실행하려면 --confirm이 필요합니다.")
        data = json.loads(read_text(path))
        if data["state"] != "active":
            raise ValueError("활성 예약이 아닙니다.")
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        if now < datetime.fromisoformat(data["due_at"]):
            return {"ran": False, "reason": "아직 예약 시각 전"}
        lock = work / "output/personal-schedule.lock"
        try:
            lock.mkdir()
        except FileExistsError:
            raise ValueError("예약 실행 중이거나 이전 실행 확인이 필요합니다.") from None
        try:
            from .documents import generate

            result = generate(
                work, data["task"], output_subdir=f"scheduled-{data['run_count'] + 1}"
            )
            data.update(
                {
                    "state": "completed",
                    "run_count": data["run_count"] + 1,
                    "last_ran_at": now.isoformat(),
                }
            )
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return result
        except Exception:
            data.update(
                state="failed-awaiting-check",
                last_attempt_at=now.isoformat(),
                error_kind="scheduled-generation-failed",
            )
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            raise
        finally:
            lock.rmdir()
    else:
        raise ValueError("알 수 없는 예약 동작입니다.")
    return json.loads(read_text(path))


def backup(workspace, destination):
    work, destination = Path(workspace).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(work):
        raise ValueError("작업 폴더 밖의 새 백업 경로를 고르세요.")
    verify(work)
    if any(p.is_symlink() for p in work.rglob("*")):
        raise ValueError("심볼릭 링크가 있는 폴더는 백업하지 않습니다.")
    if (work / "output/personal-schedule.lock").exists() or (
        work / "state/team-operation.lock"
    ).exists():
        raise ValueError("예약 실행 또는 팀 작업이 끝난 뒤 백업하세요.")
    # SQLite's backup API snapshots a live DB consistently, including committed WAL data.
    databases = [
        p for p in work.rglob("*") if p.is_file() and p.suffix in {".sqlite3", ".sqlite", ".db"}
    ]
    ignored = {
        str(p)
        for db in databases
        for p in (db, Path(str(db) + "-wal"), Path(str(db) + "-shm"), Path(str(db) + "-journal"))
    }

    def ignore(folder, names):
        return [name for name in names if str(Path(folder) / name) in ignored]

    shutil.copytree(work, destination, ignore=ignore)
    for path in databases:
        target = destination / path.relative_to(work)
        with (
            sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as original,
            sqlite3.connect(target) as snapshot,
        ):
            original.backup(snapshot)
            if snapshot.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("DB 백업 무결성 검사에 실패했습니다.")
    write_json(destination / "backup-hashes.json", hashes(destination))
    return {"backup": str(destination)}


def restore(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(source):
        raise ValueError("비어 있는 새 복구 경로를 고르세요.")
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("심볼릭 링크가 있는 백업은 복구하지 않습니다.")
    expected = json.loads(read_text(source / "backup-hashes.json"))
    actual = hashes(source)
    actual.pop("backup-hashes.json", None)
    if actual != expected:
        raise ValueError("백업 파일 해시가 다릅니다. 복구를 중단합니다.")
    shutil.copytree(source, destination)
    (destination / "backup-hashes.json").unlink()
    verify(destination)
    for path in destination.rglob("*"):
        if path.is_file() and path.suffix in {".sqlite3", ".sqlite", ".db"}:
            with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("복구한 DB 무결성 검사에 실패했습니다.")
    return {"restored": str(destination)}
