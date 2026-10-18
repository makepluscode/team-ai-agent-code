"""Chapter preparation has no implicit Git or wiki setup."""

import hashlib
import json
import shutil
from pathlib import Path

from .io import write_json

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if PACKAGE_ROOT.name == "src":
    PACKAGE_ROOT = PACKAGE_ROOT.parent


def example_path(chapter):
    group = {
        1: "documents",
        2: "documents",
        3: "documents",
        4: "wiki",
        5: "wiki",
        6: "meetings",
    }.get(chapter, "requests")
    return PACKAGE_ROOT / "examples" / group / f"ch{chapter:02}"


def hashes(folder):
    folder = Path(folder)
    return {
        p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(folder.rglob("*"))
        if p.is_file() and not p.is_symlink()
    }


def verify(workspace):
    work = Path(workspace).resolve()
    metadata = json.loads((work / ".exercise.json").read_text(encoding="utf-8"))
    for relative, expected in metadata["sources"].items():
        path = work / relative
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(work)
            or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise ValueError(f"시작 원본이 바뀌었습니다. 새 폴더에 복구하세요: {relative}")
    source_map = work / "output/source-map.json"
    if metadata["chapter"] == 2 and source_map.exists():
        report = json.loads(source_map.read_text(encoding="utf-8"))
        rows = report["files"]
        originals = {f"input/files/{p.name}" for p in (work / "input/files").iterdir()}
        if {row["source"] for row in rows} != originals or len(rows) != len(originals):
            raise ValueError("정리 대응표의 원본 파일 목록을 확인하세요.")
        targets = set()
        for row in rows:
            original, copied = work / row["source"], work / row["copy"]
            if (
                copied.is_symlink()
                or not copied.resolve().is_relative_to(work / "output/organized")
                or copied.resolve() in targets
                or not copied.is_file()
                or original.read_bytes() != copied.read_bytes()
            ):
                raise ValueError("정리본의 경로·중복·원본 바이트를 확인하세요.")
            targets.add(copied.resolve())
        if report["review_count"] != sum(
            row["copy"].startswith("output/organized/확인-필요/") for row in rows
        ):
            raise ValueError("확인 필요 건수를 확인하세요.")
    return metadata


def prepare(chapter, workspace):
    if chapter not in range(1, 13):
        raise ValueError("장은 1~12입니다.")
    source = example_path(chapter)
    if not (source / "start").is_dir():
        raise ValueError(f"시작 자료가 없습니다: {source}")
    work = Path(workspace).resolve()
    if work.exists() and (not work.is_dir() or any(work.iterdir())):
        raise ValueError(f"빈 새 폴더를 고르세요. 기존 자료를 보존합니다: {work}")
    # Reject symbolic links before copying any files.
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError("예제의 심볼릭 링크는 복사하지 않습니다.")
    work.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / "start", work, dirs_exist_ok=True)
    shutil.copytree(source / "prompts", work / "prompts", dirs_exist_ok=True)
    for name in ("input", "output"):
        (work / name).mkdir(exist_ok=True)
    originals = {
        k: v
        for k, v in hashes(work).items()
        if k.startswith(("input/", "raw/")) and k != "input/my-instructions.md"
    }
    write_json(
        work / ".exercise.json",
        {
            "chapter": chapter,
            "package_version": "1.7",
            "sources": originals,
            "data_kind": "synthetic",
            "reference_kind": "edited-reference",
            "editable_settings": ["input/my-instructions.md"]
            if (work / "input/my-instructions.md").exists()
            else [],
            "example": source.relative_to(PACKAGE_ROOT).as_posix(),
        },
    )
    return {
        "workspace": str(work),
        "chapter": chapter,
        "reference_copied": False,
        "git_initialized": False,
    }


def bundle(chapter, destination):
    """Distribute a chapter as ordinary folders; no Git account is required."""
    import tempfile
    import zipfile

    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("기존 압축 파일을 보존합니다.")
    source = example_path(chapter)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="team-work-bundle-") as temporary:
        work = Path(temporary) / f"ch{chapter:02}"
        prepare(chapter, work)
        with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(work.rglob("*")):
                archive.write(path, f"ch{chapter:02}/" + path.relative_to(work).as_posix())
            for folder in ("reference",):
                for path in sorted((source / folder).rglob("*")):
                    archive.write(
                        path,
                        f"ch{chapter:02}/reference/" + path.relative_to(source / folder).as_posix(),
                    )
            for name in ("README.md", "RECOVERY.md", "HANDOFF.md"):
                path = source / name
                if path.exists():
                    archive.write(path, f"ch{chapter:02}/{name}")
    return {
        "archive": str(destination),
        "chapter": chapter,
        "git_required": False,
        "reference_kind": "edited-reference",
        "api_executed": False,
    }
