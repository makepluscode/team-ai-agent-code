#!/usr/bin/env python3
"""Prepared daily-job entry point. Check hours, preserve dated outputs, avoid reruns.

Preview is default. --execute runs the saved job; --reference uses the authored
comparison instead of a model. OS/Hermes scheduler registration is separate.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import TASKS, business_time, prepare, read_json, run_task, verify, wiki_path


def pull_wiki(wiki):
    """First step of every scheduled job: wiki-sync pull-only. Exit code 2 means stop."""
    script = Path(wiki) / "skills/wiki-sync/scripts/wiki_sync.py"
    if not script.is_file():
        return {"wiki_pull": "skipped", "reason": "위키 동기화 스킬이 없음"}
    remote = subprocess.run(["git", "-C", str(wiki), "remote"], capture_output=True, text=True)
    if not remote.stdout.strip():
        return {"wiki_pull": "skipped", "reason": "원격 저장소가 없는 연습 위키"}
    result = subprocess.run([sys.executable, str(script), "pull-only"], cwd=wiki, capture_output=True, text=True)
    return {"wiki_pull": "stopped" if result.returncode == 2 else "ok" if result.returncode == 0 else "failed",
            "message": (result.stdout or result.stderr).strip()[:300]}


def scheduled(task_id,workspace,at=None,execute=False,reference=False,engine=None):
    workspace=Path(workspace).resolve()
    value=at or datetime.now().astimezone().isoformat()
    gate=business_time(value,read_json(workspace/"input/business-hours.json"))
    day=gate["local_time"][:10]
    task=TASKS[task_id]
    target=workspace/"scheduled"/day/task_id
    result={**gate,"task_id":task_id,"run_folder":str(target),"executed":False}
    if not gate["within_business_hours"]:
        return result
    if (target/"completed.json").exists():
        verify(task,target)
        return {**result,"action":"같은 날의 성공 결과를 보존"}
    if not execute:
        return {**result,"action":"실행안 확인. 실행하려면 --execute를 지정합니다."}
    if target.exists():
        raise ValueError("이 날짜의 미완료 실행 자료가 있습니다. 결과를 확인한 뒤 별도 작업 폴더에서 재시도합니다.")
    wiki=wiki_path(workspace)
    pulled=pull_wiki(wiki) if wiki.exists() else {"wiki_pull":"skipped","reason":"위키 없음"}
    result.update(pulled)
    if pulled["wiki_pull"] in ("stopped","failed"):
        return {**result,"action":"위키 받기에서 멈춰 작업을 실행하지 않았습니다. 멈춘 이유를 확인합니다."}
    prepare(target, wiki=wiki if wiki.exists() else None)
    output=run_task(task,target,reference,engine=engine)
    (target/"completed.json").write_text(json.dumps({"task_id":task_id,"output":str(output),"reference":reference},ensure_ascii=False)+"\n",encoding="utf-8")
    return {**result,"executed":True,"action":"결과 저장·형식 확인 완료"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--task",choices=list(TASKS),default="ch06-morning-briefing")
    p.add_argument("--workspace",type=Path,default=Path("work"))
    p.add_argument("--at",help="시간대를 포함한 연습용 시각. 실제 예약에서는 생략합니다.")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--reference",action="store_true")
    p.add_argument("--engine",choices=["hermes","api"])
    a=p.parse_args()
    try:
        print(json.dumps(scheduled(a.task,a.workspace,a.at,a.execute,a.reference,a.engine),ensure_ascii=False,indent=2))
    except (ValueError,OSError) as e:
        p.exit(1,f"확인 필요: {e}\n")


if __name__=="__main__":
    main()
