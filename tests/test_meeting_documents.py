"""Authored meeting sources, provenance and frozen report scope; no live API."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from team_work import documents, models, operations, wiki
from team_work.workspace import PACKAGE_ROOT, prepare, verify


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def mocked_response(text="테스트 응답"):
    return {"text": text, "provider": "mock", "model": "mock", "usage": None}


def test_meeting_inputs_and_independent_report_are_identical(tmp_path):
    ch2, ch3 = tmp_path / "ch2", tmp_path / "ch3"
    prepare(2, ch2)
    prepare(3, ch3)
    with pytest.raises(ValueError, match="confirm"):
        documents.organize(ch2)
    assert not (ch2 / "output/organized").exists()
    documents.organize(ch2, confirmed=True)
    report = read(ch2 / "output/source-map.json")
    reference = read(PACKAGE_ROOT / "examples/documents/ch02/reference/source-map.json")
    assert report["files"] == reference["files"]
    assert report["plan_kind"] == "provided-edited-mapping"
    assert len(report["files"]) == 8 and report["review_count"] == 1
    for row in report["files"]:
        name = Path(row["copy"]).relative_to("output/organized")
        assert (ch2 / row["source"]).read_bytes() == (ch3 / "input/organized" / name).read_bytes()
    image = ch2 / "input/files/IMG_2041.png"
    assert image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    attachment = read(ch2 / "input/attachments.json")["attachments"][0]
    assert attachment["recorded_date"] == "2026-10-05"
    assert "회의사진" in next(r["copy"] for r in report["files"] if r["source"].endswith(".png"))
    verify(ch2)
    copied = ch2 / report["files"][0]["copy"]
    copied.write_text("damaged copy", encoding="utf-8")
    with pytest.raises(ValueError, match="정리본"):
        verify(ch2)


def test_confirmed_proposal_is_distinct_and_incomplete_or_duplicate_plan_stops(tmp_path):
    work = tmp_path / "work"
    prepare(2, work)
    mapping = read(work / "input/filing-map.json")
    proposal = work / "output/proposal.json"
    missing = dict(mapping)
    missing.pop("이름 없음.txt")
    proposal.write_text(json.dumps(missing), encoding="utf-8")
    with pytest.raises(ValueError, match="빠짐없이"):
        documents.organize(work, plan="output/proposal.json", confirmed=True)
    assert not (work / "output/organized").exists()
    duplicate = dict(mapping)
    duplicate["업무 메모.md"] = duplicate["회의록 최종.md"]
    proposal.write_text(json.dumps(duplicate), encoding="utf-8")
    with pytest.raises(ValueError, match="중복"):
        documents.organize(work, plan="output/proposal.json", confirmed=True)
    assert not (work / "output/organized").exists()
    proposal.write_text(json.dumps(mapping), encoding="utf-8")
    documents.organize(work, plan="output/proposal.json", confirmed=True)
    assert read(work / "output/source-map.json")["plan_kind"] == "human-confirmed-proposal"


def test_report_sources_support_four_distinct_completions_and_keep_missing_status(tmp_path):
    work = tmp_path / "work"
    prepare(3, work)
    job = read(work / "input/jobs.json")["weekly-report"]
    assert "improvement-memo" not in read(work / "input/jobs.json")
    assert len([p for p in job["inputs"] if p.startswith("input/organized/")]) == 6
    assert not any("확인-필요" in p or p.endswith(".png") or "reference" in p for p in job["inputs"])
    texts = "\n".join((work / p).read_text(encoding="utf-8") for p in job["inputs"])
    observed = set(re.findall(r"항목키 (ITEM-\d+)[^\n]*상태 완료[^\n]*완료일 (\d{4}-\d{2}-\d{2})", texts))
    expected = read(PACKAGE_ROOT / "examples/documents/ch03/reference/weekly-report-checks.json")
    assert sorted(key for key, _ in observed) == expected["completed_item_keys"]
    assert len(observed) == expected["observed_completed_count"] == 4
    snapshot = read(work / "input/snapshot.json")
    assert all(snapshot["report_period"]["start"] <= date <= snapshot["as_of"][:10] for _, date in observed)
    assert "신규 완료 항목은 0건" in texts and "상태: （미기재）" in texts
    assert "BASE-001" in texts and "ITEM-005" in texts and "ITEM-006" in texts
    assert "2026-10-08" in texts  # A due date is allowed, not a later change event.
    assert "DOC-010" not in texts and "MTG-001" not in texts


def test_comparison_reads_organized_meetings_without_answer_input(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(2, work)
    calls = []
    monkeypatch.setattr(models, "call_commercial", lambda system, prompt: calls.append(prompt) or mocked_response())
    with pytest.raises(FileNotFoundError):
        documents.generate(work, "comparison")
    assert not calls
    documents.organize(work, confirmed=True)
    documents.generate(work, "comparison")
    assert "2026-10-02_주간회의" in calls[0] and "2026-10-05_주간회의" in calls[0]
    assert "filing-map.json" not in calls[0] and "DOC-002" not in calls[0]


def test_friday_schedule_preserves_report_snapshot(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(3, work)
    snapshot = (work / "input/snapshot.json").read_bytes()
    prompts = []
    monkeypatch.setattr(models, "call_commercial", lambda system, prompt: prompts.append(prompt) or mocked_response())
    friday = "2026-10-09T17:00:00+09:00"
    assert datetime.fromisoformat(friday).weekday() == 4
    operations.schedule(work, "create", friday)
    operations.schedule(work, "run-due", confirmed=True)
    assert (work / "input/snapshot.json").read_bytes() == snapshot
    assert '"as_of": "2026-10-07T09:00:00+09:00"' in prompts[0]
    assert "실행 시각으로 바꾸지" in prompts[0]
    assert "IMG_2041" not in prompts[0] and "이름 없음" not in prompts[0]
    assert "ITEM-001" in prompts[0] and "ITEM-006" in prompts[0]


@pytest.mark.parametrize("chapter", range(4, 13))
def test_later_chapters_preserve_report_sources_and_registry_hashes(tmp_path, chapter):
    work = tmp_path / str(chapter)
    prepare(chapter, work)
    rows = read(work / "input/report-source-map.json")
    for row in rows:
        original = PACKAGE_ROOT / row["source_path"]
        preserved = work / row["preserved_path"]
        assert preserved.read_bytes() == original.read_bytes()
        assert hashlib.sha256(preserved.read_bytes()).hexdigest() == row["sha256"]
    assert read(work / "raw/report-input/snapshot.json")["as_of"] == "2026-10-07T09:00:00+09:00"
    registry_name = "raw-registry.json" if chapter <= 6 else "source-registry.json"
    for row in read(work / "input" / registry_name):
        path = work / row.get("registered_path", row.get("preserved_path"))
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    verify(work)


def test_wiki_proposal_can_read_report_text_sources_without_images(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(4, work)
    calls = []
    def capture(system, prompt, **kwargs):
        calls.append(prompt)
        return mocked_response(json.dumps({"files": [{"path": "wiki/index.md", "content": "test"}]}))
    monkeypatch.setattr(models, "call_commercial", capture)
    wiki.propose(work)
    assert "ITEM-003" in calls[0] and "ITEM-006" in calls[0]
    assert "raw/report-input/snapshot.json" in calls[0]
    # File names in the provenance README may mention pictures; binary data is never attached.
    assert "PNG" not in calls[0]
