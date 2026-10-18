"""장별 예제 폴더(ch01~ch03)의 check.py가 기준 결과로 통과하고 원본 변경을 잡는지 확인한다."""

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# 예제 폴더 → (expected/ 안의 파일, output/ 안에 둘 이름)
SIMPLE = {
    "ch01/02-onboarding-plan": ("DOC-005_onboarding-plan.md", "DOC-005_onboarding-plan.md"),
    "ch02/03-compare-meetings": ("DOC-006_comparison.md", "DOC-006_comparison.md"),
    "ch03/01-onboarding-guide": (
        "DOC-007_onboarding-guide.r1.md",
        "DOC-007_onboarding-guide.r1.md",
    ),
    "ch03/02-weekly-report": ("DOC-009_weekly-report.r1.md", "DOC-009_weekly-report.r1.md"),
    "ch03/03-weekly-skill": ("DOC-009_weekly-report.r1.md", "DOC-009_weekly-report_skill-run.md"),
    "ch03/04-weekly-schedule": (
        "DOC-009_weekly-report.r1.md",
        f"scheduled/{date.today().isoformat()}_DOC-009_weekly-report.r1.md",
    ),
}


def run_check(folder: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "check.py"],
        check=False,
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def copy_example(tmp_path: Path, name: str) -> Path:
    target = tmp_path / name.replace("/", "_")
    shutil.copytree(ROOT / name, target, ignore=shutil.ignore_patterns("output", ".venv"))
    return target


@pytest.mark.parametrize("name", sorted(SIMPLE))
def test_simple_examples_pass_and_detect_changes(tmp_path, name):
    folder = copy_example(tmp_path, name)
    assert run_check(folder).returncode == 1  # 결과 파일이 없으면 실패
    source, result = SIMPLE[name]
    (folder / "output" / result).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(folder / "expected" / source, folder / "output" / result)
    done = run_check(folder)
    assert done.returncode == 0, done.stdout
    assert "자동 확인: 통과" in done.stdout
    # 원본을 한 글자 바꾸면 실패해야 한다
    first = min(p for p in (folder / "input").rglob("*") if p.is_file())
    first.write_bytes(first.read_bytes() + b"\n")
    assert run_check(folder).returncode == 1


def organize_like_expected(folder: Path) -> list[dict]:
    rows = json.loads((folder / "expected" / "source-map.json").read_text(encoding="utf-8"))[
        "files"
    ]
    for row in rows:
        if row["copy"]:
            (folder / row["copy"]).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(folder / row["source"], folder / row["copy"])
        row.pop("sha256")
    return rows


def write_map(folder: Path, rows: list[dict]) -> None:
    data = json.dumps({"files": rows}, ensure_ascii=False)
    (folder / "output" / "source-map.json").write_text(data, encoding="utf-8")


def test_organize_passes_with_other_topic_names(tmp_path):
    folder = copy_example(tmp_path, "ch02/02-organize-notes")
    rows = organize_like_expected(folder)
    # 주제 부분은 모델마다 달라도 된다
    first = next(r for r in rows if r["status"] == "organized")
    renamed = first["copy"].replace("주간회의.md", "주간회의_안내준비.md")
    (folder / first["copy"]).rename(folder / renamed)
    first["copy"] = renamed
    write_map(folder, rows)
    done = run_check(folder)
    assert done.returncode == 0, done.stdout


@pytest.mark.parametrize("mistake", ["wrong-date", "duplicate-copied", "moved-original"])
def test_organize_catches_mistakes(tmp_path, mistake):
    folder = copy_example(tmp_path, "ch02/02-organize-notes")
    rows = organize_like_expected(folder)
    if mistake == "wrong-date":
        row = next(r for r in rows if r["source"].endswith("IMG_2041.png"))
        wrong = row["copy"].replace("2026-10-05", "2026-10-06")
        (folder / row["copy"]).rename(folder / wrong)
        row["copy"] = wrong
    elif mistake == "duplicate-copied":
        row = next(r for r in rows if r["status"] == "duplicate")
        row["status"], row["copy"] = (
            "organized",
            "output/organized/2026-10-02_회의노트_주간회의2.md",
        )
        shutil.copy(folder / row["source"], folder / row["copy"])
    else:
        (folder / "input" / "files" / "이름 없음.txt").unlink()
    write_map(folder, rows)
    assert run_check(folder).returncode == 1


def test_schedule_ignores_old_results(tmp_path):
    folder = copy_example(tmp_path, "ch03/04-weekly-schedule")
    old = folder / "output" / "scheduled" / "2026-10-09_DOC-009_weekly-report.r1.md"
    old.parent.mkdir(parents=True)
    shutil.copy(folder / "expected" / "DOC-009_weekly-report.r1.md", old)
    assert run_check(folder).returncode == 1
