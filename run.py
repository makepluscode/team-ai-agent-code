#!/usr/bin/env python3
"""Ready-to-run exercises for chapters 2–6 (tasks in chNN/tasks.json). Python 3.10+, standard library.

Model tasks use an existing Hermes installation and a saved prompt, or call a
commercial API directly (--engine api, keys from the environment only). No
program generation is required. --reference opens an authored comparison
artifact, which is never presented as a model response or a live-service result.
prepare also creates a practice team wiki (work/wiki) that the prompts read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, time as daytime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
CHAPTERS = ["ch02", "ch03", "ch04", "ch05", "ch06"]
import llm  # noqa: E402
import wiki as team_wiki  # noqa: E402

TASKS = {t["id"]: t for chapter in CHAPTERS
         for t in json.loads((BASE / "legacy" / chapter / "tasks.json").read_text(encoding="utf-8"))["tasks"]}


def chapter_file(task, kind):
    """chNN/prompts/<id>.txt or chNN/completed/<output> of the task's own chapter."""
    folder = BASE / "legacy" / task["id"][:4]
    return folder / "prompts" / f"{task['id']}.txt" if kind == "prompt" else folder / "completed" / task["output"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def inside(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"작업 폴더 밖의 경로입니다: {relative}")
    return path


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def wiki_path(workspace):
    settings = workspace / "settings.json"
    if settings.is_file():
        return Path(read_json(settings)["wiki"])
    return workspace / "wiki"


def prepare(workspace, wiki_from="ch02", wiki=None):
    """Create input/output/prompts and, unless --wiki points elsewhere, a practice wiki."""
    workspace = Path(workspace).resolve()
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError("자료 보존을 위해 빈 작업 폴더를 지정해 주세요. 복구도 새 폴더에서 시작합니다.")
    workspace.mkdir(parents=True, exist_ok=True)
    for chapter in CHAPTERS:
        shutil.copytree(BASE / "legacy" / chapter / "start", workspace / "input", dirs_exist_ok=True)
    (workspace / "output").mkdir()
    (workspace / "prompts").mkdir()
    if wiki:
        wiki = Path(wiki).expanduser().resolve()
        if not (wiki / "AGENTS.md").is_file():
            raise ValueError(f"팀 위키 폴더가 아닙니다(AGENTS.md 없음): {wiki}")
    else:
        wiki = team_wiki.init(workspace / "wiki", wiki_from)
    write_json(workspace / "settings.json", {"wiki": str(wiki), "wiki_from": None if wiki != workspace / "wiki" else wiki_from})
    for task in TASKS.values():
        source_path = chapter_file(task, "prompt")
        if not source_path.is_file():
            continue
        text = source_path.read_text(encoding="utf-8")
        text = text.replace("{{INPUT}}", str(workspace / "input")).replace("{{WIKI}}", str(wiki))
        text = text.replace("{{OUTPUT_DIR}}", str(workspace / "output"))
        text = text.replace("{{OUTPUT}}", str(workspace / "output" / task["output"]))
        (workspace / "prompts" / f"{task['id']}.txt").write_text(text, encoding="utf-8")
    write_json(workspace / "input-hashes.json", hashes(workspace / "input"))
    print(f"준비 완료: {workspace} (위키: {wiki})")
    return workspace


def verify(task, workspace):
    workspace = Path(workspace).resolve()
    if hashes(workspace / "input") != read_json(workspace / "input-hashes.json"):
        raise ValueError("입력 파일이 달라졌습니다. 원본과 대조하거나 새 폴더에서 복구해 주세요.")
    target = inside(workspace / "output", task["output"])
    if not target.is_file() or target.stat().st_size == 0:
        raise ValueError(f"결과 파일이 없습니다: {target}")
    if target.suffix == ".json":
        read_json(target)
    text = target.read_text(encoding="utf-8")
    for keyword in task.get("required", []):  # 'a|b'는 같은 뜻의 다른 표기 중 하나만 있으면 됨
        if not any(option in text for option in keyword.split("|")):
            raise ValueError(f"결과의 필수 항목을 확인해 주세요: {keyword}")
    body = draft_part(text, task.get("forbidden_scope_end", []))
    for keyword in task.get("forbidden", []):
        if keyword in body:
            raise ValueError(f"결과에 들어가면 안 되는 내용이 있습니다: {keyword}")
    return target


def draft_part(text, markers):
    """Text before the first heading that names a non-draft section (e.g. '사용한 사실')."""
    if not markers:
        return text
    lines = text.splitlines()
    for index, line in enumerate(lines[1:], 1):
        stripped = line.strip()
        underlined = index + 1 < len(lines) and set(lines[index + 1].strip()) <= {"-", "="} and lines[index + 1].strip()
        heading = stripped.startswith("#") or (stripped.startswith("**") and stripped.endswith("**")) or underlined
        if heading and any(marker in stripped for marker in markers):
            return "\n".join(lines[:index])
    return text


def organize(workspace, rename=False):
    rows = read_json(workspace / "input/assets/manifest.json")
    mapping, destinations = [], set()
    for row in rows:
        source = inside(workspace / "input/assets", row["file"])
        if not source.is_file():
            raise ValueError(f"소재 파일 없음: {row['file']}")
        client = row.get("client_id")
        campaign = row.get("campaign_id")
        if not client or not campaign:
            destination = Path("확인-필요") / source.name
        elif rename:
            name = f"{row['date']}_{client}_{campaign}_{row['kind']}{source.suffix}"
            destination = Path(client) / campaign / name
        else:
            destination = Path(client) / campaign / source.name
        if str(destination) in destinations:
            raise ValueError(f"이름 충돌: {destination}. 대응표를 고친 뒤 다시 실행합니다.")
        destinations.add(str(destination))
        mapping.append((source, destination, bool(client and campaign)))
    folder = workspace / "output" / ("renamed" if rename else "organized")
    if folder.exists():
        raise ValueError(f"기존 결과를 보존합니다: {folder}")
    folder.mkdir()
    for source, destination, _ in mapping:
        target = inside(folder, destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return {"input_count":len(mapping), "classified_count":sum(r[2] for r in mapping),
            "review_count":sum(not r[2] for r in mapping), "originals_preserved":True,
            "mapping":[{"source":s.name,"destination":str(d)} for s,d,_ in mapping]}


def performance(workspace):
    with (workspace / "input/performance.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    summary = []
    for row in rows:
        impressions = int(row["impressions"]) if row["impressions"] else None
        clicks = int(row["clicks"]) if row["clicks"] else None
        ctr = Decimal(clicks)*100/Decimal(impressions) if impressions and clicks is not None else None
        summary.append({**row, "ctr_percent":str(ctr.quantize(Decimal("0.01"))) if ctr is not None else None})
    lines = ["# 봉봉소프트 캠페인 주간 보고", "", "합성 성과 자료의 계산 결과입니다. 실제 운영 성과가 아닙니다.",
             "", "## 집계 조건", "기간·채널·원자료: input/performance.csv. 기간이 다른 행은 따로 표시합니다.",
             "", "## 계산 결과", "| 기간 | 채널 | 노출 | 클릭 | CTR |", "|---|---|---|---|---|"]
    for row in summary:
        lines.append(f"| {row['period']} | {row['channel']} | {row['impressions'] or '확인 필요'} | {row['clicks'] or '확인 필요'} | {row['ctr_percent']+'%' if row['ctr_percent'] is not None else '확인 필요'} |")
    lines += ["", "## 확인 필요", "결측값은 0으로 채우지 않습니다. 기간이 다른 자료로 증감을 계산하지 않습니다.",
              "", "## 다음 확인", "콘텐츠·노출 대상·측정 조건을 함께 확인한 뒤 개선안을 정합니다."]
    return "\n".join(lines)+"\n"


def business_time(value, config):
    instant = datetime.fromisoformat(value)
    if instant.tzinfo is None:
        raise ValueError("시간대가 포함된 시각을 넣어 주세요. 예: 2026-10-08T09:00:00+09:00")
    local = instant.astimezone(ZoneInfo(config["timezone"]))
    opened = (local.weekday() in config["weekdays"]
              and local.date().isoformat() not in config["closed_dates"]
              and daytime.fromisoformat(config["start"]) <= local.time().replace(tzinfo=None)
              < daytime.fromisoformat(config["end"]))
    return {"timezone":config["timezone"], "local_time":local.isoformat(),
            "within_business_hours":opened,
            "action":"작업 실행 가능" if opened else "다음 업무시간까지 대기",
            "note":"이 코드는 실행 전 조건을 확인합니다. 예약 등록이나 컴퓨터 자동 시작은 별도입니다."}


def cost_summary(records, prices):
    total = Decimal("0")
    unknown = 0
    attempts = []
    rates = prices.get("rates_usd_per_million", {})
    fields = ["input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"]
    for row in records:
        known = row.get("cost_usd")
        if known is not None:
            cost = Decimal(str(known))
        elif all(row.get(f) is not None and rates.get(f) is not None for f in fields):
            cost = sum(Decimal(str(row[f]))*Decimal(str(rates[f])) for f in fields)/Decimal(1_000_000)
        else:
            cost = None
            unknown += 1
        if cost is not None:
            total += cost
        attempts.append({"attempt_id":row["attempt_id"], "task_id":row["task_id"],
                         "status":row["status"], "cost_usd":str(cost) if cost is not None else None})
    return {"data_origin": "synthetic" if any(r.get("data_origin")=="synthetic" for r in records) else "measured",
            "attempt_count":len(records), "failed_attempts":sum(r["status"]=="failed" for r in records),
            "known_subtotal_usd":str(total), "unpriced_attempts":unknown,
            "total_usd":str(total) if unknown==0 else None,
            "price_card_date":prices["checked_on"], "attempts":attempts,
            "note":"실패·재시도를 포함합니다. 미확인 단가·토큰은 null로 남깁니다."}


def services(workspace, task_id):
    """Local fixture results for 5.2~5.5. No MCP call and no external write."""
    data = read_json(workspace / "input/services.json")
    events = read_json(workspace / "input/events.json")
    thread = data["threads"][0]
    base = {"mode": "local-fixture", "client": thread["client"], "campaign_id": thread["campaign_id"],
            "external_writes": False}
    if task_id == "ch05-mail":
        confirmed = {"channel": {"value": "SNS", "source": "MSG-BB-001-2"},
                     "publish_date": {"value": "2026-10-12", "source": "MSG-BB-001-1"}}
        questions = ["최종 분량", "검수 담당자"]
        return {**base, "thread_id": thread["id"], "messages_read": [m["id"] for m in thread["messages"]],
                "confirmed": confirmed, "questions": questions,
                "draft": {"status": "draft", "location": "대표 메일함 임시보관함(연습: 로컬 파일)",
                          "body": "보내 주신 요청을 확인했습니다. 채널은 SNS, 첫 발행일은 10월 12일로 이해했습니다. "
                                  "최종 분량과 검수 담당자가 정해지면 알려 주세요. 정해지는 대로 초안에 반영하겠습니다."},
                "wiki_record": "raw/20261005_BB_CAMP-BB-202610_mail.md",
                "note": "이미 확인된 채널은 다시 묻지 않습니다. 금액·완료일은 근거가 없어 약속하지 않습니다."}
    latest = [e for e in events if e["kind"] == "confirmed_change"][-1]
    if task_id == "ch05-calendar":
        current = next(c for c in data["calendar"] if c.get("source_event_id") == latest["supersedes"])
        untouched = [c for c in data["calendar"] if c is not current]
        return {**base, "proposal": {"action": "update", "event_id": current["id"], "from": current["date"],
                                     "to": latest["effective_date"], "time": "확인 필요", "timezone": "Asia/Seoul",
                                     "source_event_id": latest["id"], "wiki_page": "wiki/campaigns/CAMP-BB-202610.md",
                                     "status": "approval_required"},
                "not_changed": [{"event_id": c["id"], "date": c["date"], "status": c["status"],
                                 "reason": "잠정 일정이라 확정으로 바꾸지 않음" if c["status"] == "tentative" else "다른 업무"}
                                for c in untouched],
                "unconfirmed": latest.get("unconfirmed", [])}
    if task_id == "ch05-notification":
        return {**base, "channel": "#studio-merry-ops", "channel_kind": "연습 채널", "status": "not_sent",
                "wiki_page": "wiki/campaigns/CAMP-BB-202610.md",
                "body": "[봉봉소프트] 채널 SNS 확정, 분량 문의 답장 초안 확인 대기 / wiki/campaigns/CAMP-BB-202610.md / "
                        "위키를 동기화하고 캠페인 페이지의 채널을 확인한 뒤 게시물 초안 형식을 맞춰 주세요.",
                "alternative": {"channel": "kakao-memo", "status": "not_sent", "note": "카카오톡 수신 범위는 확인 필요"}}
    if task_id == "ch05-document":
        first = data["documents"][0]
        return {**base, "document_id": first["id"], "wiki_page": first["wiki_page"],
                "versions": [{"version": 1, "source_event_id": first["source_event_id"], "date": "2026-10-12", "status": "변경 전(보존)"},
                             {"version": 2, "source_event_id": latest["id"], "date": latest["effective_date"], "status": "현재"}],
                "document": {"source_event_id": latest["id"], "version": 2, "date": latest["effective_date"]},
                "wiki_equivalent": "캠페인 페이지의 현재 조건(2판)과 변경 이력(1판). 위키 갱신은 ch05-wiki-record에서 합니다."}
    raise ValueError(f"알 수 없는 서비스 실습: {task_id}")


def put_guide(workspace, source, relative):
    """3.1 '위키에 넣기': guides/ in the practice wiki. Never overwrites an existing guide."""
    wiki = wiki_path(workspace)
    target = wiki / relative
    if wiki != workspace / "wiki" or target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def local_task(task, workspace, at):
    op = task["operation"]
    if op in ("organize", "rename"):
        return json.dumps(organize(workspace,op=="rename"),ensure_ascii=False,indent=2)+"\n"
    if op == "report":
        return performance(workspace)
    if op == "services":
        return json.dumps(services(workspace, task["id"]),ensure_ascii=False,indent=2)+"\n"
    if op == "drive-export":
        result = team_wiki.export(wiki_path(workspace), workspace / "output/drive-export", at=at)
        return json.dumps(result, ensure_ascii=False, indent=2)+"\n"
    if op == "costs-measured":
        path = workspace / "run-history.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []
        records = [r for r in records if r.get("mode") == "api"]
        if not records:
            raise ValueError("상용 API로 실행한 기록이 없습니다. --engine api로 모델 실습을 먼저 실행합니다.")
        result = cost_summary(records, read_json(workspace / "input/price-card.json"))
        result["data_origin"] = "measured-runner"
        result["by_provider"] = {}
        for row in records:
            key = f"{row['provider']}/{row['model']}"
            slot = result["by_provider"].setdefault(key, {"attempts": 0, "input_tokens": 0, "output_tokens": 0})
            slot["attempts"] += 1
            slot["input_tokens"] += row.get("input_tokens") or 0
            slot["output_tokens"] += row.get("output_tokens") or 0
        result["note"] = "이 작업 폴더에서 실제로 호출한 기록(measured)입니다. 가격표 단가가 null이면 합계도 null입니다."
        return json.dumps(result, ensure_ascii=False, indent=2)+"\n"
    if op == "hours":
        return json.dumps(business_time(at,read_json(workspace / "input/business-hours.json")),ensure_ascii=False,indent=2)+"\n"
    if op == "costs":
        records = [json.loads(line) for line in (workspace / "input/usage-example.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        result = cost_summary(records,read_json(workspace / "input/price-card.json"))
        result["note"] = "실패·재시도를 포함합니다. 미확인 토큰·단가는 null이며 합계도 미확정입니다."
        return json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if op == "template":
        if task["id"] == "ch03-client-guides":
            for source in (workspace / "input/brands").glob("*.md"):
                destination = workspace / "output/brands" / source.name
                destination.parent.mkdir(parents=True,exist_ok=True)
                if destination.exists():
                    raise ValueError(f"기존 고객 지침을 보존합니다: {destination}")
                shutil.copy2(source,destination)
                put_guide(workspace, source, f"guides/brands/{source.name}")
        if task["id"] == "ch03-common-style":
            put_guide(workspace, chapter_file(task, "completed"), "guides/SOUL.md")
        return chapter_file(task, "completed").read_text(encoding="utf-8")
    raise ValueError(f"알 수 없는 처리: {op}")


def record(workspace, task, status, mode, elapsed, call=None):
    usage = (call or {}).get("usage") or {}
    location = {"hermes": "unknown", "api": "cloud"}.get(mode, "application")
    row = {"attempt_id":datetime.now().astimezone().isoformat()+"-"+task["id"],
           "task_id":task["id"], "client_id":task["client_id"],
           "campaign_id":task["campaign_id"], "work_type":task["operation"],
           "processing_location":location,
           "provider":(call or {}).get("provider"),"model":(call or {}).get("model"),
           "mode":mode, "status":status, "elapsed_seconds":round(elapsed,3),
           "input_tokens":usage.get("input_tokens"),"output_tokens":usage.get("output_tokens"),
           "cache_read_tokens":usage.get("cache_read_tokens"),
           "cache_write_tokens":usage.get("cache_write_tokens"),"cost_usd":None,"attempts":(call or {}).get("attempts"),"data_origin":"measured-runner"}
    with (workspace / "run-history.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")


def engine_for(engine):
    if engine:
        return engine
    if shutil.which("hermes"):
        return "hermes"
    if llm.available():
        return "api"
    return "hermes"


def context_files(task, workspace):
    files = []
    roots = {"input": workspace / "input", "wiki": wiki_path(workspace), "output": workspace / "output"}
    for item in task.get("context", []):
        root, relative = item.split(":", 1)
        optional = relative.endswith("?")
        relative = relative.rstrip("?")
        path = roots[root] / relative
        if not path.is_file():
            if optional:
                continue
            raise ValueError(f"입력 파일이 없습니다: {path}")
        files.append((f"{path}", path))
    return files


API_ANSWER = """

# 답하는 형식
너는 파일을 직접 저장할 수 없다. 결과 파일에 들어갈 전체 내용만 답한다.
결과 파일이 .json이면 JSON만, .md이면 마크다운만 답하고 앞뒤 설명을 붙이지 않는다.
"""


def run_model(task, workspace, target, engine):
    prompt = workspace / "prompts" / f"{task['id']}.txt"
    if engine == "hermes":
        command = shutil.which("hermes")
        if not command:
            raise ValueError("헤르메스 설치·모델 연결을 확인해 주세요. API 키가 있으면 --engine api, 결과 형식만 보려면 --reference를 씁니다.")
        result = subprocess.run([command,"chat","--oneshot","--query-file",str(prompt)],cwd=workspace,check=False)
        if result.returncode:
            raise ValueError(f"헤르메스가 종료 코드 {result.returncode}로 끝났습니다. 인증·모델·작업 경로를 확인해 주세요.")
        return None
    text = prompt.read_text(encoding="utf-8") + API_ANSWER + llm.attach(context_files(task, workspace))
    call = llm.complete(text, json_output=target.suffix == ".json")
    body = llm.strip_fence(call["text"]).strip() + "\n"
    if target.suffix == ".json":
        body = json.dumps(llm.parse_json(body), ensure_ascii=False, indent=2) + "\n"
    target.write_text(body, encoding="utf-8")
    return call


def run_wiki(task, workspace, target, engine, reference):
    result = team_wiki.run(task["id"], wiki_path(workspace), workspace / "output", engine, reference)
    write_json(target, result)
    if not result["passed"]:
        raise ValueError("위키 정리 검사 실패: " + "; ".join(result["problems"]))
    usage = {k: sum((c.get("usage") or {}).get(k) or 0 for c in result["calls"]) or None
             for k in ["input_tokens", "output_tokens"]}
    first = (result["calls"] or [{}])[0]
    return {"provider": first.get("provider"), "model": first.get("model"), "usage": usage} if result["calls"] else None


def run_task(task, workspace, reference=False, at="2026-10-08T09:00:00+09:00", engine=None):
    workspace = Path(workspace).resolve()
    if not (workspace / "input-hashes.json").is_file():
        raise ValueError("먼저 prepare로 실습 자료를 준비해 주세요.")
    target = inside(workspace / "output",task["output"])
    if target.exists():
        raise ValueError(f"기존 결과를 보존합니다: {target}. 다른 작업 폴더를 선택해 주세요.")
    if hashes(workspace / "input") != read_json(workspace / "input-hashes.json"):
        raise ValueError("입력 원본이 변경됐습니다.")
    target.parent.mkdir(parents=True,exist_ok=True)
    needs_model = task["operation"] in ("model", "wiki")
    engine = engine_for(engine) if needs_model and not reference else None
    mode = "reference" if reference else engine if needs_model else "local"
    started = time.monotonic()
    call = None
    try:
        if task["operation"] == "wiki":
            call = run_wiki(task, workspace, target, engine or "api", reference)
            if reference:
                print("저자 작성 비교용 위키를 덮어 놓았습니다. 모델 정리 결과가 아닙니다.")
        elif reference and task.get("reference") is False:
            raise ValueError("이 실습은 비교용 결과가 없습니다. 자신의 실행 기록으로만 확인합니다.")
        elif reference:
            source = chapter_file(task, "completed")
            if source.is_dir() or not source.exists():
                target.write_text(local_task(task,workspace,at),encoding="utf-8")
            else:
                shutil.copy2(source,target)
            print("저자 작성 비교용 결과를 열었습니다. 모델 실행이나 외부 서비스 연결 결과가 아닙니다.")
        elif task["operation"]=="model":
            call = run_model(task, workspace, target, engine)
        else:
            target.write_text(local_task(task,workspace,at),encoding="utf-8")
        verify(task,workspace)
    except Exception:
        record(workspace,task,"failed",mode,time.monotonic()-started,call)
        raise
    record(workspace,task,"ok",mode,time.monotonic()-started,call)
    where = f" ({call['provider']}/{call['model']})" if call and call.get("provider") else ""
    print(f"형식·원본 보존 확인{where}: {target}\n내용의 사실과 고객 구분은 원자료와 직접 대조합니다.")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["list","prepare","prompt","run","check","mcp-config"])
    parser.add_argument("task",nargs="?")
    parser.add_argument("--workspace",type=Path,default=Path("work"))
    parser.add_argument("--reference",action="store_true")
    parser.add_argument("--at",default="2026-10-08T09:00:00+09:00")
    parser.add_argument("--engine",choices=["hermes","api"],help="모델 실습의 실행 경로. 생략하면 헤르메스, 없으면 API 키")
    parser.add_argument("--wiki-from",default="ch02",help="prepare가 만들 연습 위키의 시작 상태(ch02~ch09)")
    parser.add_argument("--wiki",type=Path,help="prepare: 연습 위키 대신 쓸 자신의 위키 폴더")
    args = parser.parse_args()
    try:
        if args.command == "list":
            for task in TASKS.values():
                print(task["id"],task["section"],task["title"])
        elif args.command == "prepare":
            prepare(args.workspace, args.wiki_from, args.wiki)
        elif args.command == "mcp-config":
            uv = shutil.which("uv")
            if not uv:
                raise ValueError("uv 설치를 확인해 주세요.")
            command_args = ["run","--no-project","--python","3.11","--with-requirements",str(BASE/"legacy/ch05/requirements-mcp.txt"),
                            "python",str(BASE/"legacy/ch05/mcp_server.py"),"--workspace",str(args.workspace.resolve())]
            print("mcp_servers:\n  studio_merry_practice:\n    command: "+json.dumps(uv)+"\n    args: "+json.dumps(command_args,ensure_ascii=False))
        else:
            if args.task not in TASKS:
                raise ValueError("list에서 실습 ID를 고른 뒤 명령을 실행해 주세요.")
            task = TASKS[args.task]
            if args.command == "prompt":
                if task["operation"] == "wiki":
                    wtask = team_wiki.TASKS[task["id"]]
                    for raw in wtask["raws"]:
                        print(f"# 원본 raw/{raw['name']} — 위키 폴더에서 hermes chat에 붙여 넣습니다\n")
                        print(team_wiki.ingest_prompt(wtask, raw["name"]))
                    if wtask.get("rule_lines"):
                        print("# 먼저 규칙 파일(AGENTS.md)의 '## 목록과 기록' 앞에 다음 줄을 더합니다\n" + "\n".join(wtask["rule_lines"]))
                else:
                    print((args.workspace / "prompts" / f"{task['id']}.txt").read_text(encoding="utf-8"))
            elif args.command == "check":
                print(verify(task,args.workspace))
            else:
                run_task(task,args.workspace,args.reference,args.at,args.engine)
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        parser.exit(1,f"확인 필요: {exc}\n")


if __name__ == "__main__":
    main()
