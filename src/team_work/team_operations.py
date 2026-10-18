"""팀 업무시간·근거 브리핑·단일 처리자. 수동 실행이며 헤르메스 예약 등록은 별도다."""
from __future__ import annotations

import json
import os
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from . import requests
from .workspace import verify

DEFAULT_RULES = {"timezone": "Asia/Seoul", "weekdays": [0, 1, 2, 3, 4],
                 "opens": "09:00", "closes": "18:00", "holidays": []}


def rules(workspace):
    verify(workspace)
    path = Path(workspace) / "input" / "business-hours.json"
    config = requests.read_json(path) if path.exists() else dict(DEFAULT_RULES)
    start, close = time.fromisoformat(config["opens"]), time.fromisoformat(config["closes"])
    if start >= close or not set(config["weekdays"]) <= set(range(7)):
        raise ValueError("업무시간은 같은 날짜의 시작<종료와 요일0~6이 필요합니다.")
    return config


def parse_time(value, config):
    stamp = datetime.fromisoformat(value) if value else datetime.now(UTC)
    if stamp.tzinfo is None:
        raise ValueError("시각에 시간대(+09:00 등)가 필요합니다.")
    return stamp.astimezone(ZoneInfo(config["timezone"]))


def gate(workspace, at=None):
    config = rules(workspace)
    stamp = parse_time(at, config)
    working = (stamp.weekday() in config["weekdays"] and stamp.date().isoformat() not in config.get("holidays", [])
               and time.fromisoformat(config["opens"]) <= stamp.time().replace(tzinfo=None) < time.fromisoformat(config["closes"]))
    next_open = stamp.replace(hour=time.fromisoformat(config["opens"]).hour,
                              minute=time.fromisoformat(config["opens"]).minute, second=0, microsecond=0)
    if next_open <= stamp:
        next_open += timedelta(days=1)
    for _ in range(370):
        if next_open.weekday() in config["weekdays"] and next_open.date().isoformat() not in config.get("holidays", []):
            break
        next_open += timedelta(days=1)
    else:
        raise ValueError("다음 업무일을 찾을 수 없습니다.")
    return {"at": stamp.isoformat(), "timezone": config["timezone"], "working_hours": working,
            "next_open": next_open.isoformat(), "holidays_source": "제공 설정; 공휴일 자동 조회 없음"}


def briefing(workspace, at=None):
    config = rules(workspace)
    stamp = parse_time(at, config)
    data = requests.summary(workspace)
    opening = time.fromisoformat(config["opens"])
    morning = stamp.replace(hour=opening.hour, minute=opening.minute, second=0, microsecond=0)
    # Prior workday's close through this workday's opening; weekends remain queued.
    prior = morning - timedelta(days=1)
    for _ in range(370):
        if prior.weekday() in config["weekdays"] and prior.date().isoformat() not in config.get("holidays", []):
            break
        prior -= timedelta(days=1)
    close = time.fromisoformat(config["closes"])
    prior_close = prior.replace(hour=close.hour, minute=close.minute)
    overnight_until = min(morning, stamp)
    overnight = [r for r in data["requests"] if prior_close <= datetime.fromisoformat(r["received_at"]) < overnight_until]
    pending = [t for t in data["tasks"] if t["status"] == "확인 대기"]
    overdue = [t for t in data["tasks"] if t.get("due_at") and t["status"] != "완료"
               and datetime.fromisoformat(t["due_at"]) < stamp]
    return {"at": stamp.isoformat(), "gate": gate(workspace, at), "engine": "deterministic-record-briefing",
            "overnight_window": {"from": prior_close.isoformat(), "until": overnight_until.isoformat()},
            "overnight_requests": [{"request_id": r["request_id"], "received_at": r["received_at"],
                                     "source_ref": r["source_ref"]} for r in overnight],
            "pending": [{"task_id": t["task_id"], "owner_id": t.get("owner_id"), "source_refs": t["source_refs"]} for t in pending],
            "overdue": [{"task_id": t["task_id"], "due_at": t["due_at"], "source_refs": t["source_refs"]} for t in overdue],
            "counts": data["counts"], "request_count": len(data["requests"]), "task_count": len(data["tasks"]),
            "model_call": False, "external_send": False}


def configure_owner(workspace, owner):
    verify(workspace)
    if owner not in requests.MEMBERS:
        raise ValueError("명부의 단일 팀 운영 담당자가 필요합니다.")
    path = Path(workspace) / "state" / "team-owner.json"
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        existing = requests.read_json(path)
        if existing["owner_id"] != owner:
            raise ValueError("다른 담당자가 등록되어 있습니다. 이전 담당 중지·백업 후 새 작업 폴더로 이관하세요.")
        return existing
    value = {"owner_id": owner, "wiki_actor": "wiki-curator", "registered_at": requests.now(),
             "background_schedule_registered": False, "mail_connection": "선택·실연결 TODO(검증)"}
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
    return value


@contextmanager
def owner_lock(workspace, owner):
    path = Path(workspace) / "state" / "team-owner.json"
    if not path.is_file() or requests.read_json(path)["owner_id"] != owner:
        raise ValueError("등록한 단일 운영 담당자와 일치해야 합니다.")
    lock = path.with_name("team-operation.lock")
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("팀 작업이 실행 중이거나 중단 잠금이 남았습니다. 중복 실행을 거부합니다.") from None
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump({"owner_id": owner, "pid": os.getpid(), "created_at": requests.now()}, stream)
        yield
    finally:
        lock.unlink(missing_ok=True)


def release_lock(workspace, owner, confirm=False):
    verify(workspace)
    if not confirm:
        raise ValueError("실행 프로세스 종료를 확인한 뒤 --confirm으로 잠금을 해제하세요.")
    path = Path(workspace) / "state" / "team-operation.lock"
    if path.exists() and requests.read_json(path)["owner_id"] != owner:
        raise ValueError("잠금 소유자 불일치")
    path.unlink(missing_ok=True)
    return {"released": True, "owner_id": owner}


def run_due(workspace, owner, at=None):
    status = gate(workspace, at)
    with owner_lock(workspace, owner):
        run_id = "RUN-OBS-" + uuid.uuid4().hex
        run = {"run_id": run_id, "task_id": None, "data_kind": "synthetic" if at else "observed",
               "engine": "team-record-briefing", "started_at": requests.now(), "finished_at": None,
               "status": "skipped-off-hours", "usage": None, "cost": None, "error": None,
               "simulation_at": at, "model_call": False}
        failed = False
        try:
            if status["working_hours"]:
                result = briefing(workspace, at)
                path = Path(workspace) / "output" / f"briefing-{run_id}.json"
                with path.open("x", encoding="utf-8") as stream:
                    json.dump(result, stream, ensure_ascii=False, indent=2)
                run.update(status="succeeded-record-briefing", output_ref=str(path.relative_to(Path(workspace))))
        except Exception as error:  # noqa: BLE001 - preserve failure evidence without secret exception bodies
            run.update(status="failed", error=type(error).__name__)
            failed = True
        with requests.database(workspace) as db:
            event = requests.event(db, "team-operations", owner, None, run["status"],
                     "수동 업무시간 확인; 외부 처리·모델 호출 없음", ["state/team-owner.json"], data_kind=run["data_kind"])
            run["event_id"] = event["event_id"]
            run["finished_at"] = requests.now()
            requests.save(db, "runs", run_id, run)
        if failed:
            raise ValueError("팀 실행 실패를 기록했습니다. 원인 조건을 확인하고 다시 실행하세요.")
        return {"gate": status, "run": run, "background_schedule_registered": False}


def register_parser(subparsers):
    root = subparsers.add_parser("team-ops", help="팀 업무시간·단일 담당·근거 브리핑")
    commands = root.add_subparsers(dest="team_operation", required=True)
    for action in ["gate", "briefing", "init", "run-due", "release-lock"]:
        p = commands.add_parser(action)
        p.add_argument("--workspace", type=Path, required=True)
        if action in {"gate", "briefing", "run-due"}:
            p.add_argument("--at", help="시간대를 포함한 합성 검사시각; 실제 관측과 구별")
        if action in {"init", "run-due", "release-lock"}:
            p.add_argument("--owner", required=True)
        if action == "release-lock":
            p.add_argument("--confirm", action="store_true")
        p.set_defaults(func=handle)


def handle(args):
    action = args.team_operation
    if action == "init":
        return configure_owner(args.workspace, args.owner)
    if action == "release-lock":
        return release_lock(args.workspace, args.owner, args.confirm)
    if action == "run-due":
        return run_due(args.workspace, args.owner, args.at)
    return (gate if action == "gate" else briefing)(args.workspace, args.at)
