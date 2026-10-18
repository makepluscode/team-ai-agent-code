"""Read-only SQLite MCP. Fixed SELECT tools, parameterized IDs, no write tool."""
import argparse
from pathlib import Path
from mcp.server import MCPServer
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from part3 import readonly  # noqa: E402

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--database',type=Path,required=True)
a=p.parse_args()
if not a.database.is_file():p.error('먼저 database로 조회 DB를 준비합니다.')
DB=a.database.resolve()
server=MCPServer('Studio Merry — read-only business data')

def lookup(sql,ident):
    with readonly(DB) as db:
        rows=db.execute(sql,(ident,)).fetchall()
    return {'mode':'synthetic-readonly','records':[dict(r) for r in rows],'database_writes':False}

@server.tool()
def get_inquiry(inquiry_id:str)->dict:
    """Read one synthetic inquiry by ID. Labels are not stored in this DB."""
    return lookup('SELECT id,client_id,body FROM inquiries WHERE id=?',inquiry_id)

@server.tool()
def get_customer(client_id:str)->dict:
    """Read one synthetic customer by ID."""
    return lookup('SELECT id,name FROM customers WHERE id=?',client_id)

@server.tool()
def get_price(sku:str)->dict:
    """Read a standard synthetic price by SKU. Does not calculate a quote."""
    return lookup('SELECT sku,name,unit_price_krw FROM prices WHERE sku=?',sku)

if __name__=='__main__':server.run(transport='stdio')
