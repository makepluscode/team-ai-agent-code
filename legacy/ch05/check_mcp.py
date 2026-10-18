"""Real stdio protocol smoke test of the synthetic service, no Hermes/API calls."""
import asyncio
import json
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run import prepare


async def main():
    with tempfile.TemporaryDirectory() as folder:
        work=prepare(Path(folder)/"work")
        params=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).resolve().parent/"mcp_server.py"),"--workspace",str(work)])
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as client:
                await client.initialize()
                listed=await client.list_tools()
                names={t.name for t in listed.tools}
                assert len(names)==7 and not any("send" in name for name in names),names
                async def call(name,args):
                    result=await client.call_tool(name,args)
                    assert not result.is_error,(name,result)
                    return json.loads(next(c.text for c in result.content if c.type=="text"))
                thread=await call("read_mail",{"thread_id":"THREAD-BB-001"})
                assert thread["mode"]=="local-fixture"
                await call("save_mail_draft",{"thread_id":"THREAD-BB-001","body":"확인할 초안"})
                proposal=await call("propose_calendar",{"source_event_id":"EV-BB-1008-CALL"})
                assert proposal["result"]["date"]=="2026-10-15"
                await call("write_team_document",{"document_id":"DOC-BB-001","source_event_id":"EV-BB-1008-CALL","body":"발행일을 10월 15일로 변경했습니다."})
                updated=await call("read_team_document",{"document_id":"DOC-BB-001"})
                assert updated["result"]["version"]==2
                assert updated["result"]["source_event_id"]=="EV-BB-1008-CALL"
                bad=await client.call_tool("propose_calendar",{"source_event_id":"MISSING"})
                assert bad.is_error
                print("MCP stdio: 7 tools listed; draft, calendar proposal, versioned document and invalid-source rejection passed")


asyncio.run(main())
