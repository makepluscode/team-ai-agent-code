"""Real stdio check: three SELECT tools, no writes, no evaluation labels."""
import asyncio
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('part3',BASE/'part3.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
async def main():
    with tempfile.TemporaryDirectory() as folder:
        work=app.prepare(Path(folder)/'work',with_wiki=False);db=app.build_database(work)
        params=StdioServerParameters(command=sys.executable,args=[str(BASE/'ch07/mcp_server.py'),'--database',str(db)])
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as client:
                await client.initialize()
                names={t.name for t in (await client.list_tools()).tools}
                assert names=={'get_inquiry','get_customer','get_price'},names
                async def call(name,args):
                    r=await client.call_tool(name,args);assert not r.is_error
                    return json.loads(next(c.text for c in r.content if c.type=='text'))
                row=await call('get_inquiry',{'inquiry_id':'INQ-BB-D01-A'})
                assert 'expected' not in row['records'][0] and not row['database_writes']
                price=await call('get_price',{'sku':'SNS'});assert price['records'][0]['unit_price_krw']==200000
                empty=await call('get_inquiry',{'inquiry_id':"' OR 1=1 --"});assert empty['records']==[]
                print('Part 3 MCP stdio: 3 read-only tools, no labels, price lookup, parameterized ID passed')
asyncio.run(main())
