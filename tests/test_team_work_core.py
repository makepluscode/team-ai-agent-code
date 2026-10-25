"""Safety and chapter invariants for the v1.7 path. No live API calls."""

import hashlib
import json

import pytest

from team_work import documents, models, operations, wiki
from team_work.io import write_json
from team_work.workspace import PACKAGE_ROOT, prepare, verify


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("chapter", range(1, 7))
def test_independent_start_preserves_sources_without_git(tmp_path, chapter):
    work = tmp_path / f"ch{chapter}"
    prepare(chapter, work)
    verify(work)
    assert not (work / ".git").exists()
    assert not any((work / "output").iterdir())
    assert not (work / "reference").exists()
    assert (work / "wiki").is_dir() == (chapter >= 4)
    assert (work / "raw").is_dir() == (chapter >= 4)
    with pytest.raises(ValueError):
        prepare(chapter, work)


def test_original_edit_and_symlink_are_detected(tmp_path):
    prepare(1, tmp_path / "work")
    work = tmp_path / "work"
    original = work / "input/DOC-001_onboarding.md"
    original.write_text("changed")
    with pytest.raises(ValueError, match="바뀌었"):
        verify(work)
    original.unlink()
    external = tmp_path / "external"
    external.write_text("outside")
    original.symlink_to(external)
    with pytest.raises(ValueError):
        verify(work)


def test_organize_keeps_binary_bytes_timestamp_and_unknown(tmp_path):
    work = tmp_path / "work"
    prepare(2, work)
    # Existing real source copies remain byte-for-byte identical.
    result = documents.organize(work, confirmed=True)
    assert result["copied"] == 8
    report = read(work / "output/source-map.json")
    assert report["originals_preserved"] is True
    assert report["review_count"] == 1
    mapping = report["files"]
    for row in mapping:
        original, copy = work / row["source"], work / row["copy"]
        assert original.read_bytes() == copy.read_bytes()
        assert original.stat().st_mtime_ns == copy.stat().st_mtime_ns
    assert (work / "output/organized/확인-필요/이름 없음.txt").is_file()
    with pytest.raises(ValueError):
        documents.organize(work, confirmed=True)
    verify(work)


def response(text="실제 응답을 흉내 낸 테스트 값"):
    return {
        "text": text,
        "provider": "mock",
        "model": "mock",
        "usage": {"input_tokens": 1},
        "elapsed_seconds": 0,
    }


def test_generation_records_actual_call_and_refuses_overwrite(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(1, work)
    calls = []

    def mocked(system, prompt):
        calls.append(prompt)
        return response()

    monkeypatch.setattr(models, "call_commercial", mocked)
    documents.generate(work, "onboarding-plan")
    target = work / "output/DOC-005_first-summary.md"
    assert read(target.with_suffix(".md.run.json"))["provider"] == "mock"
    assert "DOC-001" in calls[0]
    with pytest.raises(ValueError):
        documents.generate(work, "onboarding-plan")
    assert len(calls) == 1
    verify(work)


def test_failure_records_without_leaking_exception_or_creating_output(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(1, work)

    def fail(*args, **kwargs):
        raise ValueError("DO-NOT-LOG-THIS-SECRET")

    monkeypatch.setattr(models, "call_commercial", fail)
    with pytest.raises(ValueError):
        documents.generate(work, "onboarding-plan")
    record = work / "output/DOC-005_first-summary.md.run.json"
    assert read(record)["status"] == "failed"
    assert "DO-NOT-LOG" not in record.read_text()
    assert not (work / "output/DOC-005_first-summary.md").exists()
    verify(work)


def test_register_protects_new_raw_and_keeps_hash(tmp_path):
    work = tmp_path / "work"
    prepare(5, work)
    src = work / "input/DOC-010_schedule-change.md"
    result = wiki.register(work, src)
    assert result["sha256"] == hashlib.sha256(src.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        wiki.register(work, src)
    raw = work / "raw" / src.name
    raw.write_text("tampered")
    with pytest.raises(ValueError):
        verify(work)


def proposal(work, paths):
    return {
        "data_kind": "edited-test-proposal",
        "files": [
            {
                "path": relative,
                "content": content,
                "before_sha256": hashlib.sha256((work / relative).read_bytes()).hexdigest()
                if (work / relative).exists()
                else None,
            }
            for relative, content in paths
        ],
    }


def test_wiki_preflight_no_partial_changes_and_conflict_stops(tmp_path):
    work = tmp_path / "work"
    prepare(5, work)
    file = work / "wiki/decisions/onboarding.md"
    before = file.read_bytes()
    bad = proposal(work, [("wiki/decisions/onboarding.md", "new"), ("raw/evil.md", "not allowed")])
    path = tmp_path / "proposal.json"
    write_json(path, bad)
    with pytest.raises(ValueError):
        wiki.apply(work, path, True)
    assert file.read_bytes() == before
    path.unlink()
    write_json(path, proposal(work, [("wiki/decisions/onboarding.md", "new")]))
    file.write_text("changed concurrently")
    with pytest.raises(ValueError, match="충돌"):
        wiki.apply(work, path, True)
    assert file.read_text() == "changed concurrently"


def test_wiki_confirmation_and_backup(tmp_path):
    work = tmp_path / "work"
    prepare(5, work)
    path = tmp_path / "proposal.json"
    target = work / "wiki/decisions/onboarding.md"
    original = target.read_text()
    write_json(
        path, proposal(work, [("wiki/decisions/onboarding.md", "15일 날짜 확정, 시각·장소 미정")])
    )
    with pytest.raises(ValueError):
        wiki.apply(work, path)
    wiki.apply(work, path, True)
    assert (work / "output/wiki-before/decisions/onboarding.md").read_text() == original
    assert "15일" in target.read_text()
    with pytest.raises(ValueError):
        wiki.apply(work, path, True)


def test_personal_schedule_one_shot_keeps_manual_report(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(3, work)
    monkeypatch.setattr(models, "call_commercial", lambda *a, **kw: response())
    documents.generate(work, "weekly-report")
    operations.schedule(work, "create", "2020-01-01T09:00:00+09:00")
    with pytest.raises(ValueError, match="confirm"):
        operations.schedule(work, "run-due")
    operations.schedule(work, "run-due", confirmed=True)
    assert (work / "output/scheduled-1/DOC-009_weekly-report.r1.md").exists()
    assert operations.schedule(work, "status")["run_count"] == 1
    with pytest.raises(ValueError):
        operations.schedule(work, "run-due", confirmed=True)
    operations.schedule(work, "pause")
    assert operations.schedule(work, "status")["state"] == "paused"


def test_backup_restore_hash_check(tmp_path):
    work, copy, restored = [tmp_path / n for n in ("work", "backup", "restore")]
    prepare(3, work)
    operations.backup(work, copy)
    operations.restore(copy, restored)
    verify(restored)
    (copy / "input/organized/2026-10-07_상태메모_준비업무점검.txt").write_text("tampered")
    with pytest.raises(ValueError, match="해시"):
        operations.restore(copy, tmp_path / "bad-restore")


def test_claude_requires_explicit_configuration(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("TEAM_AGENT_MODEL", raising=False)
    with pytest.raises(ValueError, match="환경 변수"):
        models.call_commercial("system", "prompt")


def test_meeting_fallback_is_not_audio_verification():
    manifest = read(PACKAGE_ROOT / "examples/meetings/ch06/start/input/meeting-manifest.json")
    assert manifest["audio"] is None
    assert manifest["transcription_executed"] is False
    jobs = read(PACKAGE_ROOT / "examples/meetings/ch06/start/input/jobs.json")
    assert "input/expected-decisions.json" not in jobs["meeting-notes"]["inputs"]


def test_bundle_is_plain_folder_with_separate_references(tmp_path):
    import zipfile

    from team_work.workspace import bundle

    archive = tmp_path / "ch01.zip"
    bundle(1, archive)
    with zipfile.ZipFile(archive) as stream:
        names = stream.namelist()
        assert "ch01/input/DOC-001_onboarding.md" in names
        assert "ch01/output/" in names
        assert "ch01/reference/DOC-005_first-summary.md" in names
        assert not any("/.git/" in name or "/wiki/" in name for name in names)
        stream.extractall(tmp_path / "extracted")
    verify(tmp_path / "extracted/ch01")
    with pytest.raises(ValueError):
        bundle(1, archive)


def test_reused_wiki_sync_selected_commit_conflict_reject_and_abort(tmp_path):
    """Real Git on temporary local fixture only; no network or project commit."""
    import shutil
    import subprocess

    if not shutil.which("git"):
        pytest.skip("Git is optional for chapters 1~4")

    def git(folder, *args):
        result = subprocess.run(
            ["git", "-C", str(folder), *args], text=True, capture_output=True, check=False
        )
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    def configure(folder):
        git(folder, "config", "user.name", "synthetic fixture")
        git(folder, "config", "user.email", "fixture@example.com")
        git(folder, "config", "core.hooksPath", str(tmp_path / "no-hooks"))

    remote, curator, member = (tmp_path / name for name in ("remote.git", "curator", "member"))
    prepare(5, curator)
    git(tmp_path, "init", "--bare", str(remote))
    git(curator, "init", "-b", "main")
    configure(curator)
    git(curator, "add", ".")
    git(curator, "commit", "-m", "temporary synthetic seed")
    git(curator, "remote", "add", "origin", str(remote))
    git(curator, "push", "-u", "origin", "main")
    git(tmp_path, "clone", "-b", "main", str(remote), str(member))
    configure(member)
    (curator / "wiki/decisions/onboarding.md").write_text("curator alternative\n")
    (curator / "raw/not-selected.md").write_text("unselected fixture\n")
    assert (
        wiki.sync(
            curator, ["commit", "--message", "selected fixture", "wiki/decisions/onboarding.md"]
        )
        == 0
    )
    assert (
        git(curator, "show", "--format=", "--name-only", "HEAD") == "wiki/decisions/onboarding.md"
    )
    assert "raw/not-selected.md" in git(curator, "status", "--porcelain")
    # Pull must first stop for an uncommitted source; leave its contents untouched.
    assert wiki.sync(curator, ["pull"]) == 2
    assert (curator / "raw/not-selected.md").read_text() == "unselected fixture\n"
    (curator / "raw/not-selected.md").unlink()
    (member / "wiki/decisions/onboarding.md").write_text("member alternative\n")
    assert (
        wiki.sync(member, ["commit", "--message", "other fixture", "wiki/decisions/onboarding.md"])
        == 0
    )
    assert wiki.sync(member, ["push"]) == 0
    remote_head = git(remote, "rev-parse", "refs/heads/main")
    assert wiki.sync(curator, ["push"]) == 2
    assert git(remote, "rev-parse", "refs/heads/main") == remote_head
    assert wiki.sync(curator, ["pull"]) == 2
    assert (curator / ".git/MERGE_HEAD").exists()
    assert wiki.sync(curator, ["abort"]) == 0
    assert (curator / "wiki/decisions/onboarding.md").read_text() == "curator alternative\n"


def test_request_database_backup_restore_same_summary_with_wal(tmp_path):
    from team_work import requests

    work, copied, restored = (tmp_path / n for n in ("work", "backup", "restored"))
    prepare(11, work)
    requests.init_workspace(work)
    with requests.database(work) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE test_backup(value TEXT)")
        db.execute("INSERT INTO test_backup VALUES('committed fixture')")
    expected = requests.summary(work)
    operations.backup(work, copied)
    operations.restore(copied, restored)
    assert requests.summary(restored) == expected
    with requests.database(restored, True) as db:
        assert db.execute("SELECT value FROM test_backup").fetchone()[0] == "committed fixture"
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_backup_refuses_active_schedule(tmp_path):
    work = tmp_path / "work"
    prepare(3, work)
    (work / "output/personal-schedule.lock").mkdir()
    with pytest.raises(ValueError, match="예약 실행"):
        operations.backup(work, tmp_path / "backup")


def test_wiki_proposal_does_not_apply_and_records_call(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(4, work)
    proposal = {"files": [{"path": "wiki/decisions/onboarding.md", "content": "12일 잠정"}]}
    monkeypatch.setattr(models, "call_commercial", lambda *a, **kw: response(json.dumps(proposal)))
    wiki.propose(work)
    assert not (work / "wiki/decisions/onboarding.md").exists()
    assert read(work / "output/wiki-proposal.json")["files"][0]["before_sha256"] is None
    assert (
        read(work / "output/wiki-proposal.run.json")["status"] == "proposed-awaiting-confirmation"
    )
    wiki.apply(work, work / "output/wiki-proposal.json", True)
    assert (work / "wiki/decisions/onboarding.md").read_text().strip() == "12일 잠정"
    log = (work / "wiki/log.md").read_text()
    assert "wiki-curator · 사람 확인 후 적용 · wiki/decisions/onboarding.md" in log
    assert not (work / "output/wiki-before/log.md").exists()


def test_wiki_repeat_proposal_keeps_earlier_records(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(4, work)
    first = {"files": [{"path": "wiki/decisions/onboarding.md", "content": "12일 잠정"}]}
    monkeypatch.setattr(models, "call_commercial", lambda *a, **kw: response(json.dumps(first)))
    wiki.propose(work)
    wiki.apply(work, work / "output/wiki-proposal.json", True)
    second = {"files": [{"path": "wiki/decisions/onboarding.md", "content": "12일 잠정·주간 보고 추가"}]}
    monkeypatch.setattr(models, "call_commercial", lambda *a, **kw: response(json.dumps(second)))
    assert wiki.propose(work)["proposal"] == "output/wiki-proposal-2.json"
    assert read(work / "output/wiki-proposal.json")["files"][0]["content"] == "12일 잠정"
    wiki.apply(work, work / "output/wiki-proposal-2.json", True)
    assert "주간 보고" in (work / "wiki/decisions/onboarding.md").read_text()
    assert (work / "output/wiki-before-2/decisions/onboarding.md").read_text().strip() == "12일 잠정"
    with pytest.raises(ValueError, match="이미 적용"):
        wiki.apply(work, work / "output/wiki-proposal-2.json", True)


def test_wiki_change_during_proposal_is_not_silently_overwritten(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(5, work)

    def concurrent_change(*args, **kwargs):
        (work / "wiki/index.md").write_text("concurrent change")
        return response(json.dumps({"files": [{"path": "wiki/index.md", "content": "stale"}]}))

    monkeypatch.setattr(models, "call_commercial", concurrent_change)
    with pytest.raises(ValueError, match="충돌"):
        wiki.propose(work)
    assert (work / "wiki/index.md").read_text() == "concurrent change"
    assert read(work / "output/wiki-proposal.run.json")["status"] == "failed"
    assert not (work / "output/wiki-proposal.json").exists()


def test_personal_instructions_are_editable_settings_not_business_original(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(1, work)
    (work / "input/my-instructions.md").write_text("내 말투는 간결한 존댓말입니다.")
    verify(work)
    prompts = []

    def collect(system, prompt):
        prompts.append(prompt)
        return response()

    monkeypatch.setattr(models, "call_commercial", collect)
    documents.generate(work, "onboarding-plan")
    assert "간결한 존댓말" in prompts[0]


def test_failed_schedule_reports_check_needed_without_completing(tmp_path, monkeypatch):
    work = tmp_path / "work"
    prepare(3, work)
    operations.schedule(work, "create", "2020-01-01T09:00:00+09:00")

    def fail(*args, **kwargs):
        raise ValueError("mock timeout")

    monkeypatch.setattr(models, "call_commercial", fail)
    with pytest.raises(ValueError):
        operations.schedule(work, "run-due", confirmed=True)
    state = operations.schedule(work, "status")
    assert state["state"] == "failed-awaiting-check"
    assert state["run_count"] == 0
    assert not (work / "output/personal-schedule.lock").exists()
    assert not (work / "output/scheduled-1/DOC-009_weekly-report.r1.md").exists()


def test_claude_truncated_response_is_failure(monkeypatch):
    from team_work import llm_api as llm
    monkeypatch.setenv("TEAM_AGENT_PROVIDER", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(llm, "_post", lambda *a, **k: {"content": [{"type": "text", "text": "| 잘린"}],
                                                       "stop_reason": "max_tokens", "usage": {}})
    import pytest
    with pytest.raises(llm.ModelError, match="잘렸습니다"):
        llm.complete("보고서", retries=0)
