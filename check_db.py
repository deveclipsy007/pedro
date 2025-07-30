import sqlite3
from pathlib import Path

db_path = Path("data/enhanced_rag.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas encontradas:", tables)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Tabela {table_name}: {count} registros")
    
    conn.close()
else:
    print("Banco não encontrado!")
