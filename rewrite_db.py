import re

with open("database.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace sqlite3 imports
content = content.replace("import sqlite3", """import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()
PG_URL = os.getenv("DATABASE_URL")
connection_pool = None
try:
    if PG_URL:
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, PG_URL)
except Exception as e:
    print("PostgreSQL connection error:", e)

class PGConnectionWrapper:
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        self.commit = self._conn.commit
        self.rollback = self._conn.rollback
        
    def cursor(self):
        return self._conn.cursor()
        
    def execute(self, *args, **kwargs):
        cursor = self._conn.cursor()
        cursor.execute(*args, **kwargs)
        return cursor
        
    def close(self):
        if self._pool and self._conn:
            self._pool.putconn(self._conn)
            self._conn = None
""")

# Replace get_connection
old_get_conn = """def get_connection():
    conn = sqlite3.connect(DB_FILE, timeout=30.0, check_same_thread=False)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except sqlite3.OperationalError:
        pass
    return conn"""

new_get_conn = """def get_connection():
    if connection_pool:
        conn = connection_pool.getconn()
        return PGConnectionWrapper(conn, connection_pool)
    else:
        # Fallback to direct connection if pool fails
        conn = psycopg2.connect(PG_URL)
        return PGConnectionWrapper(conn, None)"""

content = content.replace(old_get_conn, new_get_conn)

# Replace '?' with '%s' inside execute(...) calls
# We'll use a regex that looks for execute(..., ...) and replaces ? inside the first string argument.
# A simpler and safer way for this specific file:
# Since all SQL queries are passed to .execute( "..." , ... ), we can just replace '?' with '%s' in all strings that look like SQL.
# Let's just find all execute( and replace ? with %s inside the string literal.
def replace_qmarks(match):
    return match.group(0).replace('?', '%s')

content = re.sub(r'execute\(\s*(["\']{1,3})[\s\S]*?\1', replace_qmarks, content)

# SQLite specific types in init_db
content = content.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
content = content.replace("INTEGER PRIMARY KEY", "BIGINT PRIMARY KEY")

# Error handling mapping
content = content.replace("sqlite3.OperationalError", "psycopg2.OperationalError")

with open("database.py", "w", encoding="utf-8") as f:
    f.write(content)

print("database.py rewritten successfully!")
