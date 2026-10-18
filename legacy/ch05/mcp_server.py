#!/usr/bin/env python3
"""Chapter 5's synthetic-service MCP server. No external-service credentials.

Run with: uv run --no-project --with-requirements legacy/ch05/requirements-mcp.txt
python legacy/ch05/mcp_server.py --workspace work
"""
import argparse
from pathlib import Path

from mcp.server import MCPServer

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run import read_json, write_json, inside  # noqa: E402

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--workspace",type=Path,required=True)
args=parser.parse_args()
WORK=args.workspace.resolve()
if not (WORK/"input-hashes.json").is_file():
    parser.error("먼저 run.py prepare로 작업 자료를 준비합니다.")
mcp=MCPServer("Studio Merry — local synthetic services")


def envelope(value):
    return {"mode":"local-fixture","external_writes":False,"result":value}


def save(relative,value):
    path=inside(WORK/"output/mcp",relative)
    if path.exists():
        if read_json(path)!=value:
            raise ValueError("같은 ID의 기존 초안과 내용이 다릅니다. 새 ID 또는 새 버전을 사용합니다.")
    else:
        write_json(path,value)
    return envelope({"path":str(path),**value})


@mcp.tool()
def read_mail(thread_id: str) -> dict:
    """Read a synthetic mail thread by ID. This does not connect to Gmail."""
    for thread in read_json(WORK/"input/services.json")["threads"]:
        if thread["id"]==thread_id:
            return envelope(thread)
    raise ValueError("알 수 없는 합성 스레드 ID")


@mcp.tool()
def save_mail_draft(thread_id: str, body: str) -> dict:
    """Save a local draft for a known synthetic thread. No send tool exists."""
    read_mail(thread_id)
    return save(f"mail/{thread_id}.json",dict(thread_id=thread_id,body=body,status="draft"))


@mcp.tool()
def list_calendar() -> dict:
    """Read the synthetic calendar entries. No Google Calendar connection."""
    return envelope(read_json(WORK/"input/services.json")["calendar"])


@mcp.tool()
def propose_calendar(source_event_id: str) -> dict:
    """Create a local calendar proposal from a confirmed scenario event."""
    event=next((e for e in read_json(WORK/"input/events.json") if e["id"]==source_event_id),None)
    if not event or event["kind"]!="confirmed_change":
        raise ValueError("확인된 변경 사건 ID가 필요합니다.")
    return save(f"calendar/{event['id']}.json",dict(date=event["effective_date"],source_event_id=event["id"],status="approval_required"))


@mcp.tool()
def notification_draft(channel: str, document_id: str, body: str) -> dict:
    """Create a local Slack/Kakao-style notification draft, without sending."""
    if channel not in ("slack-practice","kakao-practice") or document_id!="DOC-BB-001":
        raise ValueError("연습 채널과 연습 문서 ID를 지정합니다.")
    return save(f"notifications/{channel}.json",dict(channel=channel,document_id=document_id,body=body,status="not_sent"))


@mcp.tool()
def read_team_document(document_id: str) -> dict:
    """Read the newest synthetic team-document version and its source."""
    if document_id!="DOC-BB-001":
        raise ValueError("연습 문서 ID를 지정합니다.")
    versions=list((WORK/"output/mcp/documents").glob(f"{document_id}-v*.json"))
    if versions:
        newest=max((read_json(p) for p in versions),key=lambda d:d["version"])
        return envelope(newest)
    return envelope(read_json(WORK/"input/services.json")["documents"][0])


@mcp.tool()
def write_team_document(document_id: str, source_event_id: str, body: str) -> dict:
    """Append a local document version with a source event; preserve old versions."""
    previous=read_team_document(document_id)["result"]
    event=next((e for e in read_json(WORK/"input/events.json") if e["id"]==source_event_id),None)
    if not event:
        raise ValueError("출처 사건이 없습니다.")
    version=previous["version"]+1
    return save(f"documents/{document_id}-v{version}.json",dict(id=document_id,version=version,source_event_id=source_event_id,body=body,date=event["effective_date"]))


if __name__=="__main__":
    mcp.run(transport="stdio")
