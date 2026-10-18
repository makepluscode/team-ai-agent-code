"""Preserve sources, organize copies, and request a commercial document."""

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from . import models
from .io import read_text, write_json, write_new
from .workspace import verify

SYSTEM = (
    "스튜디오 메리의 합성 업무 자료를 읽습니다. 자료의 사실·제안·미정을 분리하고 원본 경로와 버전을 적으세요. "
    "매니저의 이름을 만들지 마세요. 응답은 제공 코드가 결과 파일에 그대로 저장합니다. "
    "저장·열기 안내나 앞뒤 설명, 바깥 코드 울타리 없이 마크다운 문서 본문만 출력하세요."
)


def generate(workspace, task, *, output_subdir=None, transcript=None):
    work = Path(workspace).resolve()
    verify(work)
    jobs = json.loads(read_text(work / "input/jobs.json"))
    if task not in jobs:
        raise ValueError("사용 가능한 업무: " + ", ".join(jobs))
    job = jobs[task]
    job = dict(job)
    if transcript is not None:
        if task != "meeting-notes":
            raise ValueError("--transcript는 meeting-notes 업무에만 씁니다.")
        path = Path(transcript).resolve()
        if not path.is_relative_to(work) or not path.is_file():
            raise ValueError("작업 폴더 안의 실제 전사문 경로를 고르세요.")
        job["inputs"] = [path.relative_to(work).as_posix()] + job["inputs"][1:]
    target = (work / "output" / (output_subdir or "") / job["output"]).resolve()
    if not target.is_relative_to(work / "output") or target.exists():
        raise ValueError("결과 경로가 잘못됐거나 기존 결과가 있습니다. 새 작업 폴더를 쓰세요.")
    attachments = []
    for relative in job["inputs"]:
        path = (work / relative).resolve()
        if not path.is_relative_to(work):
            raise ValueError("작업 폴더 밖 입력입니다.")
        attachments.append(f"\n## {relative}\n{read_text(path)}")
    prompt = read_text(work / "prompts" / job["prompt"])
    log = target.with_suffix(target.suffix + ".run.json")
    if log.exists():
        raise ValueError("기존 실행 기록을 보존합니다. 새 작업 폴더를 쓰세요.")
    record = {
        "data_kind": "observed",
        "artifact_kind": "execution-log",
        "run_id": "RUN-OBS-" + uuid.uuid4().hex,
        "task_id": job.get("task_id"),
        "task": task,
        "created_at": datetime.now(UTC).isoformat(),
        "inputs": job["inputs"],
        "status": "failed",
        "provider": None,
        "model": None,
        "usage": None,
    }
    try:
        response = models.call_commercial(SYSTEM, prompt + "\n".join(attachments))
        record.update(
            {k: response.get(k) for k in ("provider", "model", "usage", "elapsed_seconds")}
        )
        if not isinstance(response.get("text"), str) or not response["text"].strip():
            raise ValueError("빈 응답입니다.")
        verify(work)
        write_new(target, response["text"] + "\n")
        record.update(
            {"status": "generated-awaiting-review", "artifact_kind": "actual-model-output"}
        )
    except Exception:
        # Do not copy exception messages: a remote API might echo secrets or source text.
        record["error_kind"] = "generation-or-validation-failed"
        write_json(log, record)
        raise
    write_json(log, record)
    return {"saved": str(target), "business_status": "확인 대기"}


def organize(workspace, *, plan=None, confirmed=False):
    work = Path(workspace).resolve()
    verify(work)
    if not confirmed:
        raise ValueError("대응표를 확인한 뒤 --confirm으로 복사하세요.")
    plan_path = (work / (plan or "input/filing-map.json")).resolve()
    if not plan_path.is_relative_to(work) or not plan_path.is_file():
        raise ValueError("작업 폴더 안의 대응표를 고르세요.")
    mapping = json.loads(read_text(plan_path))
    if not isinstance(mapping, dict) or not mapping or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()
    ):
        raise ValueError("대응표는 원래 파일명과 정리본 이름의 JSON 객체여야 합니다.")
    originals = {p.name for p in (work / "input/files").iterdir() if p.is_file()}
    if set(mapping) != originals:
        raise ValueError("대응표는 원본 파일을 빠짐없이 한 번씩 포함해야 합니다.")
    reasons_path = work / "input/filing-reasons.json"
    reasons = json.loads(read_text(reasons_path)) if reasons_path.exists() else {}
    target = work / "output/organized"
    if target.exists():
        raise ValueError("기존 정리본을 보존합니다.")
    # Validate the entire plan before creating files.
    rows = []
    for source, destination in mapping.items():
        src, dst = (work / "input/files" / source).resolve(), (target / destination).resolve()
        if (
            (work / "input/files" / source).is_symlink()
            or not src.is_relative_to(work / "input/files")
            or not dst.is_relative_to(target)
            or not src.is_file()
        ):
            raise ValueError("파일 대응표 경로를 확인하세요.")
        rows.append((src, dst, source, destination))
    if len({row[1] for row in rows}) != len(rows):
        raise ValueError("정리본 이름이 중복됩니다.")
    for src, dst, _, _ in rows:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("xb") as stream:
            stream.write(src.read_bytes())
        shutil.copystat(src, dst)
    files = [
        {
            "source": f"input/files/{source}",
            "copy": f"output/organized/{destination}",
            "status": "needs_review" if destination.startswith("확인-필요/") else "organized",
            "reason": (
                "본문·첨부 목록의 근거와 목적지를 사람이 확인한 제안"
                if plan else reasons.get(source, "제공 편집 대응표의 분류")
            ),
        }
        for _, _, source, destination in rows
    ]
    write_json(
        work / "output/source-map.json",
        {
            "data_kind": "observed",
            "artifact_kind": "deterministic-file-operation",
            "plan_kind": "human-confirmed-proposal" if plan else "provided-edited-mapping",
            "plan": plan_path.relative_to(work).as_posix(),
            "human_confirmed": True,
            "originals_preserved": True,
            "review_count": sum(item["status"] == "needs_review" for item in files),
            "files": files,
        },
    )
    verify(work)
    return {"copied": len(rows), "originals_preserved": True}
