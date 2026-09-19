import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = "users.db"
PG_URL = os.getenv("DATABASE_URL")

def get_sqlite_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def migrate():
    if not PG_URL:
        print("❌ Xatolik: .env faylida DATABASE_URL ko'rsatilmagan!")
        return

    print("🔌 PostgreSQL ga ulanmoqda...")
    try:
        pg_conn = psycopg2.connect(PG_URL)
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"❌ PostgreSQL ga ulanishda xatolik: {e}")
        return

    print("🔌 SQLite bazasiga ulanmoqda...")
    if not os.path.exists(SQLITE_DB):
        print(f"❌ {SQLITE_DB} fayli topilmadi!")
        return
        
    sl_conn = sqlite3.connect(SQLITE_DB)
    sl_cursor = sl_conn.cursor()

    # PostgreSQL'da jadvallarni yaratish (agar yo'q bo'lsa)
    print("📝 PostgreSQL jadvallari yaratilmoqda...")
    pg_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            registered_at TIMESTAMP,
            is_premium INTEGER DEFAULT 0,
            daily_requests INTEGER DEFAULT 0,
            last_request_date DATE,
            medicine_score INTEGER DEFAULT 0,
            premium_until TIMESTAMP,
            waiting_receipt INTEGER DEFAULT 0,
            blood_group TEXT,
            age INTEGER,
            weight REAL,
            height REAL,
            chronic_diseases TEXT,
            allergies TEXT,
            premium_expires_at TIMESTAMP,
            daily_tips_subscribed INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            banned_until TIMESTAMP,
            full_name TEXT,
            username TEXT,
            free_ai_used INTEGER DEFAULT 0,
            daily_streak INTEGER DEFAULT 0,
            last_checkin_date TEXT,
            referred_by BIGINT,
            last_spin_date TEXT,
            has_discount INTEGER DEFAULT 0,
            pending_spin_prize INTEGER
        )
    ''')

    pg_cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            medicine_name TEXT,
            times TEXT,
            days TEXT DEFAULT 'daily',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP
        )
    ''')
    pg_conn.commit()

    tables = ["users", "reminders"]
    
    for table in tables:
        print(f"\n🔄 '{table}' jadvalidan ma'lumotlar o'qilmoqda...")
        columns = get_sqlite_columns(sl_cursor, table)
        
        sl_cursor.execute(f"SELECT * FROM {table}")
        rows = sl_cursor.fetchall()
        
        if not rows:
            print(f"⚠️ '{table}' jadvali bo'sh. O'tkazib yuborilmoqda...")
            continue
            
        print(f"📦 Jami {len(rows)} ta qator topildi. PostgreSQL ga yozilmoqda...")
        
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        
        if table == "users":
            insert_query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT (user_id) DO NOTHING"
        else:
            insert_query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"

        count = 0
        for row in rows:
            try:
                pg_cursor.execute(insert_query, row)
                count += 1
            except Exception as e:
                print(f"⚠️ Xatolik qatorni yozishda ({row}): {e}")
                pg_conn.rollback()
                continue
                
        pg_conn.commit()
        print(f"✅ '{table}' jadvali muvaffaqiyatli ko'chirildi! ({count}/{len(rows)})")
        
        if table == "reminders":
            try:
                pg_cursor.execute("SELECT setval('reminders_id_seq', (SELECT MAX(id) FROM reminders))")
                pg_conn.commit()
            except Exception:
                pg_conn.rollback()

    sl_conn.close()
    pg_conn.close()
    print("\n🎉 Barcha ma'lumotlar muvaffaqiyatli PostgreSQL'ga ko'chirildi!")
    print("Endi bot kodi PostgreSQL'dan foydalanishga tayyor.")

if __name__ == "__main__":
    migrate()
