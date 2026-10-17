"""위키 동기화 실행 파일 시험. 두 팀원이 같은 저장소를 쓰는 상황을 로컬 Git 저장소로 만듭니다.

    python3 -m unittest discover -s ch02/tests -v     # code 폴더에서
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

STARTER = Path(__file__).resolve().parents[1] / "wiki-starter"
SCRIPT = "skills/wiki-sync/scripts/wiki_sync.py"


def run(cwd, *args, env=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=env)


def sync(cwd, *args, env=None):
    return run(cwd, "python3", SCRIPT, *args, env=env)


class WikiSyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        run(self.tmp, "git", "init", "-q", "--bare", "-b", "main", "remote.git")
        self.pm = self.tmp / "pm"
        shutil.copytree(STARTER, self.pm)
        for cmd in (["git", "init", "-q", "-b", "main"], ["git", "config", "user.name", "PM"],
                    ["git", "config", "user.email", "pm@studiomerry.example"], ["git", "add", "-A"],
                    ["git", "commit", "-qm", "[PM] 시작"], ["git", "remote", "add", "origin", "../remote.git"],
                    ["git", "push", "-qu", "origin", "main"]):
            self.assertEqual(run(self.pm, *cmd).returncode, 0, cmd)
        run(self.tmp, "git", "clone", "-q", "remote.git", "plan")
        self.plan = self.tmp / "plan"
        run(self.plan, "git", "config", "user.name", "기획")
        run(self.plan, "git", "config", "user.email", "plan@studiomerry.example")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, root, rel, text):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_commit_only_chosen_files_and_ignore_secrets(self):
        self.write(self.pm, "wiki/clients/BB.md", "# 봉봉소프트\n")
        self.write(self.pm, "wiki/index.md", "- BB\n")
        self.write(self.pm, ".env", "KEY=x\n")
        self.assertEqual(sync(self.pm, "commit", "-m", "[PM] BB", ".env").returncode, 1)
        self.assertEqual(sync(self.pm, "commit", "-m", "[PM] BB", "wiki/clients/BB.md").returncode, 0)
        committed = run(self.pm, "git", "show", "--name-only", "--format=").stdout.split()
        self.assertEqual(committed, ["wiki/clients/BB.md"])
        self.assertEqual(sync(self.pm, "pull").returncode, 2, "기록하지 않은 index.md가 있으면 받기를 멈춤")

    def test_commit_stops_when_other_files_already_staged(self):
        self.write(self.pm, "wiki/clients/BB.md", "# 봉봉소프트\n")
        self.write(self.pm, "wiki/index.md", "- BB\n")
        run(self.pm, "git", "add", "wiki/index.md")  # 사람이나 다른 도구가 먼저 올려 둔 파일
        result = sync(self.pm, "commit", "-m", "[PM] BB", "wiki/clients/BB.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("wiki/index.md", result.stdout)
        self.assertEqual(run(self.pm, "git", "log", "-1", "--format=%s").stdout.strip(), "[PM] 시작", "기록하지 않음")

    def test_staged_rename_needs_both_paths(self):
        (self.pm / "wiki/clients").mkdir(parents=True, exist_ok=True)
        moved = run(self.pm, "git", "mv", "raw/20261005_BB_brief.md", "wiki/clients/BB.md")  # 다른 도구가 옮겨 둔 경우
        self.assertEqual(moved.returncode, 0, moved.stderr)
        result = sync(self.pm, "commit", "-m", "[PM] 이동", "wiki/clients/BB.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("raw/20261005_BB_brief.md", result.stdout)
        result = sync(self.pm, "commit", "-m", "[PM] 이동", "wiki/clients/BB.md", "raw/20261005_BB_brief.md")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_merge_accepts_conflict_resolved_to_mine_when_chosen(self):
        self._conflict("guides/brands/BB.md")
        run(self.plan, "git", "checkout", "--ours", "guides/brands/BB.md")
        run(self.plan, "git", "add", "guides/brands/BB.md")
        result = sync(self.plan, "commit", "-m", "[기획] 내 판 유지", "guides/brands/BB.md")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_pull_only_receives_and_stops_when_not_clean(self):
        self.write(self.pm, "wiki/clients/BB.md", "# 봉봉소프트\n")
        sync(self.pm, "commit", "-m", "[PM] BB", "wiki/clients/BB.md")
        self.assertEqual(sync(self.pm, "push").returncode, 0)
        self.assertEqual(sync(self.plan, "pull-only").returncode, 0)
        self.assertTrue((self.plan / "wiki/clients/BB.md").exists())
        self.write(self.plan, "raw/20261006_BB_note.md", "메모\n")
        self.assertEqual(sync(self.plan, "pull-only").returncode, 2)
        sync(self.plan, "commit", "-m", "[기획] 메모", "raw/20261006_BB_note.md")
        self.assertEqual(sync(self.plan, "pull-only").returncode, 2, "올리지 않은 기록이 있으면 멈춤")

    def test_conflict_stops_and_nothing_is_lost(self):
        self.write(self.pm, "guides/brands/BB.md", "금지: 혁신\n")
        sync(self.pm, "commit", "-m", "[PM] 금지", "guides/brands/BB.md")
        sync(self.pm, "push")
        self.write(self.plan, "guides/brands/BB.md", "금지: 최고\n")
        sync(self.plan, "commit", "-m", "[기획] 금지", "guides/brands/BB.md")
        self.assertEqual(sync(self.plan, "push").returncode, 2, "거부되면 멈춤")
        result = sync(self.plan, "pull")
        self.assertEqual(result.returncode, 2)
        self.assertIn("guides/brands/BB.md", result.stdout)
        self.assertEqual(sync(self.plan, "push").returncode, 2, "충돌 중에는 올리지 않음")
        self.assertEqual(sync(self.plan, "abort").returncode, 0)
        self.assertEqual((self.plan / "guides/brands/BB.md").read_text(encoding="utf-8"), "금지: 최고\n")
        sync(self.plan, "pull")
        self.write(self.plan, "guides/brands/BB.md", "금지: 혁신\n금지: 최고\n")
        self.assertEqual(sync(self.plan, "commit", "-m", "[기획] 합침", "guides/brands/BB.md").returncode, 0)
        self.assertEqual(sync(self.plan, "push").returncode, 0)
        sync(self.pm, "pull")
        self.assertEqual((self.pm / "guides/brands/BB.md").read_text(encoding="utf-8"), "금지: 혁신\n금지: 최고\n")
        log = run(self.pm, "git", "log", "--format=%an").stdout.split()
        self.assertIn("PM", log)
        self.assertIn("기획", log)

    def test_korean_path_commit(self):
        self.write(self.pm, "raw/20261007_BB_통화메모.md", "# 통화\n")
        result = sync(self.pm, "commit", "-m", "[PM] 통화 원본", "raw")
        self.assertEqual(result.returncode, 0, result.stdout)
        committed = run(self.pm, "git", "-c", "core.quotePath=false", "show", "--name-only", "--format=").stdout.split()
        self.assertEqual(committed, ["raw/20261007_BB_통화메모.md"])

    def test_merge_commit_rejects_unapproved_local_file(self):
        self.write(self.pm, "guides/brands/BB.md", "금지: 혁신\n")
        self.write(self.pm, "wiki/index.md", "- PM 목록\n")
        sync(self.pm, "commit", "-m", "[PM] 금지", "guides/brands/BB.md", "wiki/index.md")
        sync(self.pm, "push")
        self.write(self.plan, "guides/brands/BB.md", "금지: 최고\n")
        sync(self.plan, "commit", "-m", "[기획] 금지", "guides/brands/BB.md")
        self.assertEqual(sync(self.plan, "pull").returncode, 2)
        self.write(self.plan, "guides/brands/BB.md", "금지: 혁신\n금지: 최고\n")
        self.write(self.plan, "wiki/log.md", "몰래 바꾼 줄\n")
        run(self.plan, "git", "add", "wiki/log.md")  # 합치기 도중 다른 도구가 올려 둔 파일
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "guides/brands/BB.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("wiki/log.md", result.stdout)
        run(self.plan, "git", "reset", "-q", "wiki/log.md")
        self.write(self.plan, "wiki/index.md", "- PM 목록\n- 몰래 덧붙인 줄\n")
        run(self.plan, "git", "add", "wiki/index.md")  # 팀이 바꾼 파일을 합치기 도중 다시 고친 경우
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "guides/brands/BB.md")
        self.assertEqual(result.returncode, 2, "팀 변경 위에 덧붙인 내용도 승인 없이 기록하지 않음: " + result.stdout)
        self.assertIn("wiki/index.md", result.stdout)
        self.write(self.plan, "wiki/index.md", "- PM 목록\n")
        run(self.plan, "git", "add", "wiki/index.md")
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "guides/brands/BB.md")
        self.assertEqual(result.returncode, 0, "받아 온 그대로의 index.md는 합치기와 함께 기록됨: " + result.stdout)
        self.assertFalse((self.plan / ".git" / "wiki-sync-merge-index.json").exists())

    def test_merge_commit_rejects_unapproved_deletion_of_conflict_file(self):
        self.write(self.pm, "guides/brands/BB.md", "금지: 혁신\n")
        self.write(self.pm, "wiki/index.md", "- PM 목록\n")
        sync(self.pm, "commit", "-m", "[PM] 금지", "guides/brands/BB.md", "wiki/index.md")
        sync(self.pm, "push")
        self.write(self.plan, "guides/brands/BB.md", "금지: 최고\n")
        sync(self.plan, "commit", "-m", "[기획] 금지", "guides/brands/BB.md")
        self.assertEqual(sync(self.plan, "pull").returncode, 2)
        run(self.plan, "git", "rm", "-q", "guides/brands/BB.md")  # 충돌 파일을 다른 도구가 지운 경우
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "wiki/index.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("guides/brands/BB.md", result.stdout)

    def _conflict(self, path):
        self.write(self.pm, path, "금지: 혁신\n")
        self.write(self.pm, "wiki/index.md", "- PM 목록\n")
        sync(self.pm, "commit", "-m", "[PM] 금지", path, "wiki/index.md")
        sync(self.pm, "push")
        self.write(self.plan, path, "금지: 최고\n")
        sync(self.plan, "commit", "-m", "[기획] 금지", path)
        self.assertEqual(sync(self.plan, "pull").returncode, 2)

    def test_merge_rejects_conflict_resolved_to_mine_without_approval(self):
        self._conflict("guides/brands/BB.md")
        run(self.plan, "git", "checkout", "--ours", "guides/brands/BB.md")
        run(self.plan, "git", "add", "guides/brands/BB.md")  # 내 판 그대로 정리(바뀐 내용 없음)
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "wiki/index.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("guides/brands/BB.md", result.stdout)

    def test_merge_rejects_deleting_conflict_file_with_space(self):
        self._conflict("guides/brands/BB notes.md")
        run(self.plan, "git", "rm", "-q", "guides/brands/BB notes.md")
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "wiki/index.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("BB notes.md", result.stdout)

    def test_merge_rejects_mode_change_on_team_file(self):
        self._conflict("guides/brands/BB.md")
        self.write(self.plan, "guides/brands/BB.md", "금지: 혁신\n금지: 최고\n")
        run(self.plan, "git", "update-index", "--chmod=+x", "wiki/index.md")
        result = sync(self.plan, "commit", "-m", "[기획] 합침", "guides/brands/BB.md")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("wiki/index.md", result.stdout)

    def test_revert_keeps_history(self):
        self.write(self.pm, "wiki/clients/BB.md", "# 잘못 정리\n")
        sync(self.pm, "commit", "-m", "[PM] 잘못", "wiki/clients/BB.md")
        bad = run(self.pm, "git", "log", "-1", "--format=%h").stdout.strip()
        self.assertEqual(sync(self.pm, "revert", bad).returncode, 0)
        self.assertFalse((self.pm / "wiki/clients/BB.md").exists())
        subjects = run(self.pm, "git", "log", "--format=%s").stdout
        self.assertIn("[PM] 잘못", subjects)
        self.assertIn("Revert", subjects)

    def test_soul_check_and_apply_with_backup(self):
        home = self.tmp / "hermes_home"
        home.mkdir()
        (home / "SOUL.md").write_text("예전 말투\n", encoding="utf-8")
        self.write(self.pm, "guides/SOUL.md", "새 말투\n")
        env = {**os.environ, "HERMES_HOME": str(home)}
        self.assertEqual(sync(self.pm, "soul-check", env=env).returncode, 2)
        self.assertEqual(sync(self.pm, "soul-apply", env=env).returncode, 0)
        self.assertEqual((home / "SOUL.md").read_text(encoding="utf-8"), "새 말투\n")
        self.assertTrue(list(home.glob("SOUL.md.bak-*")))
        self.assertEqual(sync(self.pm, "soul-check", env=env).returncode, 0)


if __name__ == "__main__":
    unittest.main()
