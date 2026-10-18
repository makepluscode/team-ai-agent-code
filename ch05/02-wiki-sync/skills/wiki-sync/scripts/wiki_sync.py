#!/usr/bin/env python3
"""팀 위키 동기화 실행 파일. 위키 동기화 스킬이 이 파일만 부릅니다.

사람이 고른 파일만 기록하고, 받아 오기·올리기에서 문제가 생기면 멈춥니다.
강제 올리기(force push)와 충돌 자동 해결은 하지 않습니다. Python 3.10 이상, 표준 라이브러리만 씁니다.

    python3 wiki_sync.py status
    python3 wiki_sync.py commit --message "[PM] 봉봉소프트 페이지 추가" wiki/clients/BB.md wiki/index.md
    python3 wiki_sync.py pull
    python3 wiki_sync.py push
    python3 wiki_sync.py pull-only          # 예약 실행용 받기 전용
    python3 wiki_sync.py abort              # 충돌로 멈춘 받아 오기 취소
    python3 wiki_sync.py soul-check | soul-apply
    python3 wiki_sync.py history <파일>
    python3 wiki_sync.py revert <기록 ID>

종료 코드: 0 정상, 1 사용 오류, 2 사람의 확인이 필요해 멈춤(충돌·거부·변경 있음).
"""
from __future__ import annotations

import argparse
import json
import difflib
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

STOP = 2


def git(*args, check=True):
    # 한글 경로가 따옴표·이스케이프로 바뀌지 않게 한다(core.quotePath=false)
    result = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result


def find_root(start):
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=start, text=True, capture_output=True)
    if result.returncode:
        sys.exit("위키 폴더(Git 저장소) 안에서 실행해 주세요.")
    return Path(result.stdout.strip())


def changed_files():
    """(상태, 경로) 목록. 제외 목록(.gitignore)에 걸린 파일은 나오지 않습니다."""
    rows = []
    # 이름 변경은 삭제와 추가로 나눠 보여 준다(사람이 이전 경로의 삭제도 고르게)
    for line in git("status", "--porcelain=v1", "--untracked-files=all", "--no-renames").stdout.splitlines():
        code, path = line[:2], line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        rows.append((code, path.strip('"')))
    return rows


def index_entries():
    """기록 대기(stage 0) 파일의 {경로: 내용 해시}."""
    rows = {}
    for item in git("ls-files", "-s", "-z").stdout.split("\0"):
        if item:
            meta, path = item.split("\t", 1)
            mode, blob, stage = meta.split()
            if stage == "0":
                rows[path] = f"{mode} {blob}"  # 내용과 함께 실행 권한 같은 파일 모드도 비교한다
    return rows


def snapshot_path():
    return ROOT / ".git" / "wiki-sync-merge-index.json"


def merging():
    return (ROOT / ".git" / "MERGE_HEAD").exists()


def conflicts():
    return [n for n in git("diff", "--name-only", "--diff-filter=U", "-z").stdout.split("\0") if n]


def upstream_counts():
    """(내 쪽에만 있는 기록 수, 저장소에만 있는 기록 수). 원격이 없으면 None."""
    if git("rev-parse", "--abbrev-ref", "@{u}", check=False).returncode:
        return None
    ahead, behind = git("rev-list", "--left-right", "--count", "HEAD...@{u}").stdout.split()
    return int(ahead), int(behind)


def cmd_status(args):
    fetched = git("fetch", "--quiet", check=False).returncode == 0
    print(f"위키 폴더: {ROOT}")
    if merging():
        print("받아 오기가 충돌로 멈춘 상태입니다. 부딪친 파일:", ", ".join(conflicts()) or "(없음)")
    rows = changed_files()
    print("기록하지 않은 변경:" if rows else "기록하지 않은 변경: 없음")
    for code, path in rows:
        print(f"  {code} {path}")
    counts = upstream_counts()
    if counts is None:
        print("저장소 연결: 없음(받아 오기·올리기 불가)")
    else:
        note = "" if fetched else " (저장소에 연결하지 못해 마지막으로 받은 기준)"
        print(f"올리지 않은 내 기록: {counts[0]}개 / 받지 않은 팀 기록: {counts[1]}개{note}")
    return 0


def cmd_commit(args):
    if merging():
        print("충돌 정리 중입니다. 남길 버전을 정한 파일을 기록하면 받아 온 변경과 합치기가 끝납니다.")
        left = [p for p in conflicts() if p not in args.files]
        if left:
            print("아직 남길 버전을 정하지 않은 파일이 있습니다:", ", ".join(left)); return STOP
    if not args.message.strip():
        print("기록 문구가 비어 있습니다."); return 1
    available = {path for _, path in changed_files()}
    if merging() and snapshot_path().exists():  # 내 버전 그대로 정리해 목록에서 사라진 충돌 파일도 고를 수 있다
        available |= set(json.loads(snapshot_path().read_text(encoding="utf-8"))["conflicts"])
    chosen = [p for p in args.files]
    missing = [p for p in chosen if p not in available and not any(a.startswith(p.rstrip("/") + "/") for a in available)]
    if missing:
        print("바뀐 파일 목록에 없는 경로입니다(제외 목록 대상이거나 변경 없음):", ", ".join(missing))
        return 1
    def inside(path):
        return any(path == p or path.startswith(p.rstrip("/") + "/") for p in chosen)

    def names(*diff):
        return [n for n in git("diff", "--name-only", "--no-renames", "-z", *diff).stdout.split("\0") if n]

    # 합치기 중에는 받아 온 팀 기록이 바꾼 파일을, 받아 온 직후의 내용 그대로일 때만 함께 기록한다
    team, snap, fought = set(), {}, set()
    if merging():
        base = git("merge-base", "HEAD", "MERGE_HEAD").stdout.strip()
        team = set(names(base, "MERGE_HEAD"))
        if snapshot_path().exists():
            saved = json.loads(snapshot_path().read_text(encoding="utf-8"))
            snap, fought = saved["index"], set(saved["conflicts"])  # 충돌 파일은 언제나 사람이 고른 것만 기록
            unchosen = sorted(p for p in fought if not inside(p))
            if unchosen:  # 충돌 파일은 어떻게 정리됐든(내 버전 그대로·삭제 포함) 사람이 명시해야 한다
                print("충돌했던 파일은 직접 골라 기록해야 합니다:", ", ".join(unchosen)); return STOP
        else:
            team = set()  # 이 실행 파일 밖에서 시작한 합치기는 모든 기록 대기 파일을 사람이 고른 것으로만 인정

    def extra():
        now = index_entries()
        return [p for p in names("--cached")
                if not inside(p) and not (p in team and p not in fought and snap.get(p) == now.get(p))]

    if extra():
        print("고르지 않은 파일이 이미 기록 대기 상태입니다. 기록하지 않고 멈춥니다:", ", ".join(extra()))
        return STOP
    # -A: 고른 경로의 삭제도 기록한다. 이미 삭제가 기록 대기인 경로는 더할 것이 없으므로 뺀다
    addable = [p for p in chosen if (ROOT / p).exists() or git("ls-files", "--", p).stdout.strip()]
    if addable:
        git("add", "-A", "--", *addable)
    if extra():  # 커밋 직전 대조: 승인 목록 밖 파일이 끼면 기록하지 않는다
        print("승인 목록 밖 파일이 기록 대기에 들어갔습니다. 기록하지 않고 멈춥니다:", ", ".join(extra()))
        return STOP
    git("commit", "-m", args.message)
    snapshot_path().unlink(missing_ok=True)
    print("기록했습니다:", git("log", "-1", "--format=%h %an %s").stdout.strip())
    left = changed_files()
    if left:
        print("기록하지 않고 남긴 변경:", ", ".join(p for _, p in left))
    return 0


def cmd_pull(args):
    if merging():
        print("이미 충돌로 멈춘 상태입니다. 남길 버전을 정해 기록하거나 abort로 취소합니다."); return STOP
    rows = changed_files()
    if rows:
        print("기록하지 않은 변경이 있어 받아 오기를 멈춥니다. 먼저 고른 파일을 기록하거나 제외합니다:")
        for code, path in rows:
            print(f"  {code} {path}")
        return STOP
    before = git("rev-parse", "HEAD").stdout.strip()
    result = git("pull", "--no-rebase", "--no-edit", check=False)
    if result.returncode:
        if merging():
            print("같은 부분을 서로 다르게 고친 파일이 있어 멈췄습니다. 부딪친 파일:")
            for path in conflicts():
                print(f"  {path}")
            print("파일 안의 <<<<<<< 와 >>>>>>> 사이에 두 버전이 있습니다. 남길 버전을 사람이 정합니다.")
            # 자동으로 합쳐진 팀 변경의 내용을 기억해 두고, 기록할 때 그 뒤에 바뀐 파일을 걸러 낸다
            snapshot_path().write_text(json.dumps({"index": index_entries(), "conflicts": conflicts()},
                                                  ensure_ascii=False), encoding="utf-8")
            return STOP
        print("받아 오지 못했습니다:", (result.stderr or result.stdout).strip()); return STOP
    after = git("rev-parse", "HEAD").stdout.strip()
    if before == after:
        print("받아 온 변경이 없습니다.")
    else:
        print("받아 온 변경:")
        print(git("log", "--format=  %h %an %s", f"{before}..{after}").stdout.rstrip())
    return 0


def cmd_push(args):
    if merging() or changed_files():
        print("정리하지 않은 변경이나 충돌이 있어 올리지 않습니다. status로 확인합니다."); return STOP
    result = git("push", check=False)
    if result.returncode:
        print("저장소가 올리기를 거부했습니다. 다른 팀원의 새 기록이 있을 수 있으니 pull부터 다시 합니다.")
        print((result.stderr or result.stdout).strip())
        return STOP
    print("올렸습니다.")
    return 0


def cmd_pull_only(args):
    if merging() or changed_files():
        print("받기 전용: 기록하지 않은 변경이나 충돌이 있어 아무것도 하지 않았습니다."); return STOP
    counts = upstream_counts()
    if counts and counts[0]:
        print("받기 전용: 올리지 않은 내 기록이 있어 아무것도 하지 않았습니다."); return STOP
    result = git("pull", "--ff-only", check=False)
    if result.returncode:
        print("받기 전용: 이력이 갈라져 받아 오지 않았습니다.", (result.stderr or result.stdout).strip()); return STOP
    print("받기 전용: 받아 왔습니다." if "Already up to date" not in result.stdout else "받기 전용: 받아 온 변경이 없습니다.")
    return 0


def cmd_abort(args):
    if not merging():
        print("취소할 받아 오기가 없습니다."); return 0
    git("merge", "--abort")
    snapshot_path().unlink(missing_ok=True)
    print("받아 오기를 취소하고 받기 전 상태로 되돌렸습니다.")
    return 0


def soul_paths():
    home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    return ROOT / "guides" / "SOUL.md", home / "SOUL.md"


def cmd_soul_check(args):
    wiki, local = soul_paths()
    if not wiki.exists():
        print("위키에 guides/SOUL.md가 없습니다."); return 0
    old = local.read_text(encoding="utf-8").splitlines() if local.exists() else []
    new = wiki.read_text(encoding="utf-8").splitlines()
    if old == new:
        print("적용한 SOUL.md가 위키와 같습니다."); return 0
    print(f"위키의 SOUL.md와 적용한 파일이 다릅니다(적용한 파일: {local}). 적용하려면 soul-apply를 실행합니다.")
    print("\n".join(difflib.unified_diff(old, new, str(local), "guides/SOUL.md", lineterm="")))
    return STOP


def cmd_soul_apply(args):
    wiki, local = soul_paths()
    local.parent.mkdir(parents=True, exist_ok=True)
    if local.exists():
        backup = local.with_name(f"SOUL.md.bak-{datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(local, backup)
        print("기존 파일을 보관했습니다:", backup)
    shutil.copy2(wiki, local)
    print("적용했습니다:", local)
    return 0


def cmd_history(args):
    print(git("log", "--format=%h %ad %an %s", "--date=short", "-n", str(args.n), "--", args.path).stdout.rstrip() or "기록이 없습니다.")
    return 0


def cmd_revert(args):
    if merging() or changed_files():
        print("정리하지 않은 변경이 있어 되돌리지 않습니다."); return STOP
    result = git("revert", "--no-edit", args.commit, check=False)
    if result.returncode:
        git("revert", "--abort", check=False)
        print("되돌리는 중 다른 변경과 부딪쳐 멈추고 원래대로 두었습니다. 사람이 확인합니다."); return STOP
    print("되돌린 기록을 새로 남겼습니다:", git("log", "-1", "--format=%h %s").stdout.strip())
    print("다른 팀원에게도 반영하려면 push를 실행합니다.")
    return 0


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    c = sub.add_parser("commit"); c.add_argument("--message", "-m", required=True); c.add_argument("files", nargs="+")
    for name in ["pull", "push", "pull-only", "abort", "soul-check", "soul-apply"]:
        sub.add_parser(name)
    h = sub.add_parser("history"); h.add_argument("path"); h.add_argument("-n", type=int, default=10)
    r = sub.add_parser("revert"); r.add_argument("commit")
    args = parser.parse_args()
    ROOT = find_root(Path.cwd())
    handler = globals()["cmd_" + args.command.replace("-", "_")]
    try:
        sys.exit(handler(args))
    except RuntimeError as exc:
        print("Git 명령이 실패했습니다:", exc)
        sys.exit(STOP)


ROOT = Path.cwd()

if __name__ == "__main__":
    main()
