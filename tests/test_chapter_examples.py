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


# ── 4~12장 예제: main.py가 부르는 제공 코드 단계와 check.py ─────────────

sys.path.insert(0, str(ROOT / "src"))
from team_work.cli import main as team_work


def run(folder: Path, *args: str) -> int:
    """main.py와 같은 방식으로 제공 코드를 부른다(작업 폴더 = 예제 폴더)."""
    import os

    here = os.getcwd()
    os.chdir(folder)
    try:
        return team_work([*args, "--workspace", str(folder)])
    finally:
        os.chdir(here)


def copy_expected_wiki(folder: Path) -> None:
    shutil.copytree(folder / "expected" / "wiki", folder / "output" / "wiki-draft")


@pytest.mark.parametrize("name", ["ch04/02-first-page", "ch05/03-change-memo", "ch06/03-decision-wiki"])
def test_wiki_examples_apply_draft(tmp_path, name):
    folder = copy_example(tmp_path, name)
    if name != "ch04/02-first-page":
        source = "input/DOC-010_schedule-change.md" if "ch05" in name else "input/DOC-012_meeting-notes.md"
        assert run(folder, "wiki", "register", "--source", source) == 0
    copy_expected_wiki(folder)
    assert run(folder, "wiki", "apply-draft") == 0
    done = run_check(folder)
    assert done.returncode == 0, done.stdout
    # 두 번째 변경안도 적용되고 기준 상태가 갱신된다
    copy_expected_wiki(folder)
    assert run(folder, "wiki", "apply-draft") == 0
    assert (folder / "output" / "wiki-applied-2.json").exists()
    # 적용 뒤 위키를 직접 고치면 다음 적용은 충돌로 멈춘다
    (folder / "wiki" / "index.md").write_text("# 직접 고친 목록\n", encoding="utf-8")
    copy_expected_wiki(folder)
    with pytest.raises(SystemExit):
        run(folder, "wiki", "apply-draft")


def test_ch07_intake_counts(tmp_path):
    folder = copy_example(tmp_path, "ch07/03-mail-input")
    for args in (["requests", "init"], ["requests", "intake", "--input", "input/internal-requests.json"],
                 ["requests", "intake", "--input", "input/optional-mail.json"]):
        assert run(folder, *args) == 0
    (folder / "output").mkdir()
    (folder / "output" / "requests-all.json").write_text("[]", encoding="utf-8")
    done = run_check(folder)
    assert done.returncode == 0, done.stdout


def test_ch08_hermes_classification_import(tmp_path):
    folder = copy_example(tmp_path, "ch08/01-classify-requests")
    assert run(folder, "requests", "init") == 0
    # 편집 예시를 그대로 가져오면 합성 자료가 실제 결과로 바뀌므로 거부한다
    shutil.copytree(folder / "expected" / "classification", folder / "output" / "classification")
    with pytest.raises(SystemExit):
        run(folder, "requests", "classify", "--hermes-dir", "output/classification")
    # 헤르메스가 쓴 것처럼 합성 표식을 뺀 파일은 기록된다
    for path in (folder / "output" / "classification").glob("REQ-*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("data_kind", "artifact_kind", "request_id"):
            data.pop(key, None)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    assert run(folder, "requests", "classify", "--hermes-dir", "output/classification") == 0
    done = run_check(folder)
    assert done.returncode == 0, done.stdout
    assert "성공한 헤르메스 실행에 연결된 판정: 10건" in done.stdout
    # 같은 판정을 다시 기록해도 현재 판정 기준이라 통과한다
    assert run(folder, "requests", "classify", "--hermes-dir", "output/classification") == 0
    assert run_check(folder).returncode == 0
    # 근거가 원문에 없는 판정이 하나라도 있으면 명령이 실패하고 check.py도 실패한다
    bad = folder / "output" / "classification" / "REQ-003.json"
    data = json.loads(bad.read_text(encoding="utf-8"))
    bad.write_text(json.dumps(data | {"evidence": "원문에 없는 문장"}, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit):
        run(folder, "requests", "classify", "--hermes-dir", "output/classification")
    assert run_check(folder).returncode == 1
    # 담당 후보가 비었거나 확인 이유가 문자열이 아니면 거부한다
    from team_work.requests import validate_classification

    good = json.loads((folder / "output" / "classification" / "REQ-001.json").read_text(encoding="utf-8"))
    for broken in ({"owner_candidates": []}, {"confirmation_reason": {"x": 1}}):
        with pytest.raises(ValueError):
            validate_classification(good | broken)


def test_ch09_reviews_and_transitions(tmp_path):
    folder = copy_example(tmp_path, "ch09/02-review-and-fix")
    assert run(folder, "requests", "init") == 0
    (folder / "output").mkdir()
    for path in (folder / "expected" / "review-corrections").iterdir():
        shutil.copy(path, folder / "output" / path.name)
    for rid, actor in {"REV-001": "M01", "REV-002": "M01", "REV-003": "M01", "REV-004": "M05",
                       "REV-005": "M01", "REV-006": "M01"}.items():
        assert run(folder, "requests", "review", "--input", f"input/reviews/{rid}.json", "--actor", actor,
                   "--human-confirmed") == 0
    for status, actor, expected, extra in [("수정 필요", "M01", "확인 대기", []), ("진행", "M02", "수정 필요", []),
                                           ("확인 대기", "M02", "진행", []), ("완료", "M01", "확인 대기", ["--human-confirmed"])]:
        assert run(folder, "requests", "transition", "--task-id", "TASK-002", "--status", status, "--actor", actor,
                   "--reason", "시험", "--source-ref", "raw/DOC-012_r1.md#decision-01", "--expected", expected, *extra) == 0
    done = run_check(folder)
    assert done.returncode == 0, done.stdout


def test_ch10_structured_answers_match(tmp_path):
    folder = copy_example(tmp_path, "ch10/01-revision-search")
    from team_work.requests import qa_check

    result = qa_check(folder)
    assert result["ok"], result


def test_ch12_backup_restore(tmp_path):
    folder = copy_example(tmp_path, "ch12/03-hours-backup")
    assert run(folder, "requests", "init") == 0
    assert run(folder, "team-ops", "init", "--owner", "M01") == 0
    assert run(folder, "team-ops", "run-due", "--owner", "M01", "--at", "2026-10-30T17:30:00+09:00") == 0
    assert team_work(["backup", "--source", str(folder), "--destination", str(tmp_path / "backup")]) == 0
    assert team_work(["restore", "--source", str(tmp_path / "backup"), "--destination", str(tmp_path / "restored")]) == 0
    assert (tmp_path / "restored" / "state" / "requests.sqlite3").exists()


def test_examples_are_generated_from_specs(tmp_path):
    """명세에서 다시 만들면 저장소의 예제 폴더와 같은지 본다(손으로 고친 흔적 방지)."""
    import subprocess

    names = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("ch1[0-2]/*") if p.is_dir())
    names += sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("ch0[4-9]/*") if p.is_dir())
    assert len(names) == 27

    def files(base, n):
        return {p.relative_to(base / n).as_posix(): p.read_bytes() for p in (base / n).rglob("*")
                if p.is_file() and not {".venv", "output", "state"} & set(p.relative_to(base / n).parts)}

    # 저장소의 예제 폴더는 지우지 않고 임시 폴더에 만들어 비교한다
    subprocess.run([sys.executable, "tools/make_chapter_examples.py", "--out", str(tmp_path)],
                   cwd=ROOT, check=True, capture_output=True)
    for n in names:
        assert files(ROOT, n) == files(tmp_path, n), n
