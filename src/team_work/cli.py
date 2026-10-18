"""uv run team-work: safe preparation and feature-oriented exercises."""

import argparse
import json
from pathlib import Path

from . import documents, meetings, operations, wiki
from .workspace import bundle, prepare, verify


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare", help="장의 독립 시작 자료를 새 폴더에 준비")
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.set_defaults(func=lambda a: prepare(a.chapter, a.workspace))
    p = commands.add_parser("bundle", help="일반 폴더 실습 압축 자료 생성")
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p.set_defaults(func=lambda a: bundle(a.chapter, a.destination))
    p = commands.add_parser("verify", help="시작 원본 해시 검사")
    p.add_argument("--workspace", type=Path, required=True)
    p.set_defaults(func=lambda a: verify(a.workspace))
    p = commands.add_parser("documents", help="원본 보존과 상용 파일 생성")
    p.add_argument("action", choices=["generate", "organize"])
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--task")
    p.add_argument("--transcript", type=Path)
    p.set_defaults(
        func=lambda a: (
            documents.organize(a.workspace)
            if a.action == "organize"
            else documents.generate(a.workspace, a.task, transcript=a.transcript)
        )
    )
    p = commands.add_parser("wiki", help="명시적 원본 등록·정리 제안·사람 확인")
    p.add_argument("action", choices=["register", "propose", "apply", "search"])
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--source", type=Path)
    p.add_argument("--proposal", type=Path)
    p.add_argument("--query")
    p.add_argument("--confirm", action="store_true")

    def wiki_action(a):
        if a.action == "register":
            if not a.source:
                raise ValueError("--source가 필요합니다.")
            return wiki.register(a.workspace, a.source)
        if a.action == "propose":
            return wiki.propose(a.workspace)
        if a.action == "apply":
            if not a.proposal:
                raise ValueError("--proposal이 필요합니다.")
            return wiki.apply(a.workspace, a.proposal, a.confirm)
        return wiki.search(a.workspace, a.query or "")

    p.set_defaults(func=wiki_action)
    p = commands.add_parser("wiki-sync", help="기존 wiki-sync 제공 스킬 연결")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("arguments", nargs=argparse.REMAINDER)
    p.set_defaults(func=lambda a: wiki.sync(a.workspace, a.arguments))
    p = commands.add_parser("meetings", help="선택 실제 로컬 전사")
    p.add_argument("action", choices=["transcribe"])
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--audio", type=Path, required=True)
    p.set_defaults(func=lambda a: meetings.transcribe(a.workspace, a.audio))
    p = commands.add_parser("schedule", help="개인 예약 한 건; 제공 실행기는 직접 호출")
    p.add_argument("action", choices=["create", "status", "pause", "run-due"])
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--at")
    p.add_argument("--confirm", action="store_true")
    p.set_defaults(func=lambda a: operations.schedule(a.workspace, a.action, a.at, a.confirm))
    for name, fn in (("backup", operations.backup), ("restore", operations.restore)):
        p = commands.add_parser(name)
        p.add_argument("--source", type=Path, required=True)
        p.add_argument("--destination", type=Path, required=True)
        p.set_defaults(func=lambda a, fn=fn: fn(a.source, a.destination))
    p = commands.add_parser("reference", help="편집 비교 결과 위치 표시; 결과 폴더에 복사하지 않음")
    p.add_argument("--chapter", type=int, required=True)
    from .workspace import example_path

    p.set_defaults(
        func=lambda a: {
            "kind": "edited-reference",
            "path": str(example_path(a.chapter) / "reference"),
            "model_output": False,
        }
    )
    from . import requests, team_operations

    requests.register_parser(commands)
    team_operations.register_parser(commands)
    return root


def main(argv=None):
    root = parser()
    args = root.parse_args(argv)
    try:
        result = args.func(args)
        if isinstance(result, int):
            return result
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    except (ValueError, FileNotFoundError, KeyError, OSError) as error:
        root.exit(1, f"확인 필요: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
