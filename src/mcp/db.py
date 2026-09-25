import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "company.db"

def init_db(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        company TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        contract_title TEXT NOT NULL,
        amount INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)
    
    # 샘플 데이터가 없으면 삽입
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        customers = [
            ("김철수", "에이아이솔루션", "chulsoo.kim@aisol.com", "010-1234-5678"),
            ("이영희", "넥스트커머스", "yh.lee@nextcom.co.kr", "010-9876-5432"),
            ("박민호", "클라우드랩스", "minho@cloudlabs.net", "010-5555-8888"),
        ]
        cursor.executemany("INSERT INTO customers (name, company, email, phone) VALUES (?, ?, ?, ?)", customers)
        
        contracts = [
            (1, "LLM 인프라 구축 라이선스", 45000000, "계약완료", "2026-08-15"),
            (2, "사내 위키 연동 개발 용역", 28000000, "진행중", "2026-09-01"),
            (3, "보안 감사 컨설팅 1차", 12000000, "검토중", "2026-09-20"),
        ]
        cursor.executemany("INSERT INTO contracts (customer_id, contract_title, amount, status, created_at) VALUES (?, ?, ?, ?, ?)", contracts)
        
    conn.commit()
    conn.close()

def query_customer_contracts(keyword: str, db_path: Path = DB_PATH) -> list[dict]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
    SELECT c.name, c.company, c.email, c.phone, ct.contract_title, ct.amount, ct.status, ct.created_at
    FROM customers c
    JOIN contracts ct ON c.id = ct.customer_id
    WHERE c.name LIKE ? OR c.company LIKE ? OR ct.contract_title LIKE ?
    """
    param = f"%{keyword}%"
    cursor.execute(query, (param, param, param))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
