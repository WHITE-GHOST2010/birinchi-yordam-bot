import sqlite3
import datetime

DB_FILE = "users.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    """Ma'lumotlar bazasini yaratish"""
    conn = get_connection()
    c = conn.cursor()
    
    # Asosiy users jadvali
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            registered_at TIMESTAMP,
            is_premium INTEGER DEFAULT 0,
            daily_requests INTEGER DEFAULT 0,
            last_request_date DATE
        )
    ''')
    
    # Dori eslatmalari jadvali (Feature 2)
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            medicine_name TEXT,
            times TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP
        )
    ''')
    
    # Dinamik tarzda yangi ustunlarni qo'shamiz (avvalgi bazalar buzilmasligi uchun)
    new_columns = [
        ("waiting_receipt", "INTEGER DEFAULT 0"),
        # Feature 1: Tibbiy profil
        ("blood_group", "TEXT"),
        ("age", "INTEGER"),
        ("weight", "REAL"),
        ("height", "REAL"),
        ("chronic_diseases", "TEXT"),
        ("allergies", "TEXT"),
        # Feature 6: Premium muddati
        ("premium_expires_at", "TIMESTAMP"),
        # Feature 7: Kunlik tavsiyalar obunasi
        ("daily_tips_subscribed", "INTEGER DEFAULT 0"),
        # Ban tizimi
        ("is_banned", "INTEGER DEFAULT 0"),
        ("banned_until", "TIMESTAMP"),
        # Foydalanuvchi ismi va username
        ("full_name", "TEXT"),
        ("username", "TEXT"),
        # 1 ta bepul AI savol tizimi
        ("free_ai_used", "INTEGER DEFAULT 0"),
    ]
    
    for col_name, col_type in new_columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass  # Ustun allaqachon mavjud
        
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────
# ASOSIY FOYDALANUVCHI FUNKSIYALARI
# ─────────────────────────────────────────────────────────────────

def register_user(user_id, full_name=None, username=None):
    """Foydalanuvchini bazaga qo'shish (agar yo'q bo'lsa), ismini yangilash"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        now = datetime.datetime.now()
        c.execute(
            "INSERT INTO users (user_id, registered_at, is_premium, daily_requests, last_request_date, full_name, username) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, now.isoformat(), 0, 0, now.date().isoformat(), full_name, username)
        )
    else:
        # Ismini yangilaymiz
        if full_name or username:
            c.execute(
                "UPDATE users SET full_name=?, username=? WHERE user_id=?",
                (full_name, username, user_id)
            )
    conn.commit()
    conn.close()

def check_ai_limit(user_id) -> bool:
    """
    Foydalanuvchining AI limitsini tekshirish.
    Qaytaradi: True (ruxsat), False (limit tugagan).
    """
    register_user(user_id)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT registered_at, is_premium, daily_requests, last_request_date, premium_expires_at FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False
        
    registered_at_str, is_premium, daily_requests, last_request_date_str, premium_expires_at = row
    
    # 1. Premium foydalanuvchilar uchun muddatni tekshirish
    if is_premium:
        if premium_expires_at:
            expires = datetime.datetime.fromisoformat(premium_expires_at)
            if datetime.datetime.now() > expires:
                # Premium muddati tugagan — avtomatik o'chiramiz
                conn2 = get_connection()
                conn2.execute("UPDATE users SET is_premium = 0 WHERE user_id = ?", (user_id,))
                conn2.commit()
                conn2.close()
            else:
                return True
        else:
            return True  # Muddatsiz premium
        
    now = datetime.datetime.now()
    registered_at = datetime.datetime.fromisoformat(registered_at_str)
    
    # 2. Birinchi 24 soat mutlaqo bepul
    if (now - registered_at).total_seconds() < 24 * 3600:
        return True
        
    # 3. Kunlik limitni tekshirish
    current_date = now.date().isoformat()
    if last_request_date_str != current_date:
        conn = get_connection()
        conn.execute("UPDATE users SET daily_requests = 0, last_request_date = ? WHERE user_id = ?", (current_date, user_id))
        conn.commit()
        conn.close()
        daily_requests = 0
        
    # Kunlik bepul 5 ta so'rov
    if daily_requests >= 5:
        return False
        
    return True

def increment_usage(user_id):
    """Foydalanuvchi qidiruv sonini bittaga oshirish"""
    conn = get_connection()
    conn.execute("UPDATE users SET daily_requests = daily_requests + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def check_free_ai_used(user_id) -> bool:
    """
    Foydalanuvchi 1 ta bepul AI savolini ishlatganini tekshirish.
    Qaytaradi: True (allaqachon ishlatgan), False (hali ishlatmagan).
    Premium foydalanuvchilar uchun har doim False (limit yo'q).
    """
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_premium, premium_expires_at, free_ai_used FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    is_premium, premium_expires_at, free_ai_used = row
    # Premium tekshirish
    if is_premium:
        if premium_expires_at:
            expires = datetime.datetime.fromisoformat(premium_expires_at)
            if datetime.datetime.now() <= expires:
                return False  # Premium — limit yo'q
        else:
            return False  # Muddatsiz premium
    return bool(free_ai_used)

def set_free_ai_used(user_id):
    """Foydalanuvchining bepul AI savolini ishlatgan deb belgilash"""
    register_user(user_id)
    conn = get_connection()
    conn.execute("UPDATE users SET free_ai_used = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_premium(user_id, status: int, months: int = 1):
    """Adminga foydalanuvchini Premium qilish uchun. months - necha oylik."""
    conn = get_connection()
    if status == 1:
        expires_at = (datetime.datetime.now() + datetime.timedelta(days=30 * months)).isoformat()
        conn.execute(
            "UPDATE users SET is_premium = ?, premium_expires_at = ? WHERE user_id = ?",
            (status, expires_at, user_id)
        )
    else:
        conn.execute(
            "UPDATE users SET is_premium = ?, premium_expires_at = NULL WHERE user_id = ?",
            (status, user_id)
        )
    conn.commit()
    conn.close()

def get_premium_info(user_id):
    """Premium holati va muddatini olish"""
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_premium, premium_expires_at FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row if row else (0, None)

def set_waiting_receipt(user_id, status: int):
    """Foydalanuvchining to'lov chekini kutish holatini o'zgartirish"""
    register_user(user_id)
    conn = get_connection()
    conn.execute("UPDATE users SET waiting_receipt = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def get_waiting_receipt(user_id) -> int:
    """Foydalanuvchi to'lov chekini kutish holatini olish"""
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT waiting_receipt FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_all_users():
    """Barcha foydalanuvchilar ro'yxatini olish"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_all_users_info(limit=20):
    """Foydalanuvchilar ro'yxatini id, premium holati, ism va username bilan olish"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT user_id, is_premium, registered_at, full_name, username FROM users ORDER BY registered_at DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return rows  # [(user_id, is_premium, registered_at, full_name, username), ...]

def get_users_count():
    """Jami foydalanuvchilar soni"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_premium_count():
    """Jami premium foydalanuvchilar soni"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

# ─────────────────────────────────────────────────────────────────
# FEATURE 1: TIBBIY PROFIL
# ─────────────────────────────────────────────────────────────────

def save_medical_profile(user_id, blood_group=None, age=None, weight=None, height=None,
                          chronic_diseases=None, allergies=None):
    """Tibbiy profilni saqlash"""
    register_user(user_id)
    conn = get_connection()
    conn.execute(
        """UPDATE users SET blood_group=?, age=?, weight=?, height=?,
           chronic_diseases=?, allergies=? WHERE user_id=?""",
        (blood_group, age, weight, height, chronic_diseases, allergies, user_id)
    )
    conn.commit()
    conn.close()

def get_medical_profile(user_id):
    """Tibbiy profilni olish"""
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT blood_group, age, weight, height, chronic_diseases, allergies FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()
    return row  # (blood_group, age, weight, height, chronic_diseases, allergies)

def update_profile_field(user_id, field: str, value):
    """Tibbiy profilning bitta maydonini yangilash"""
    allowed = ["blood_group", "age", "weight", "height", "chronic_diseases", "allergies"]
    if field not in allowed:
        return
    register_user(user_id)
    conn = get_connection()
    conn.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────
# FEATURE 2: DORI ESLATMALARI
# ─────────────────────────────────────────────────────────────────

def add_reminder(user_id, medicine_name: str, times: str) -> int:
    """Yangi dori eslatmasini qo'shish. times = '08:00,14:00,20:00' ko'rinishida"""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute(
        "INSERT INTO reminders (user_id, medicine_name, times, is_active, created_at) VALUES (?, ?, ?, 1, ?)",
        (user_id, medicine_name, times, now)
    )
    reminder_id = c.lastrowid
    conn.commit()
    conn.close()
    return reminder_id

def get_user_reminders(user_id):
    """Foydalanuvchining barcha faol eslatmalari"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, medicine_name, times FROM reminders WHERE user_id = ? AND is_active = 1",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows  # [(id, name, times), ...]

def delete_reminder(reminder_id: int, user_id: int):
    """Eslatmani o'chirish"""
    conn = get_connection()
    conn.execute("UPDATE reminders SET is_active = 0 WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    conn.close()

def get_all_active_reminders():
    """Barcha faol eslatmalar (scheduler uchun)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, user_id, medicine_name, times FROM reminders WHERE is_active = 1")
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────────────────────────
# FEATURE 7: KUNLIK TAVSIYALAR OBUNASI
# ─────────────────────────────────────────────────────────────────

def set_daily_tips_subscription(user_id, status: int):
    """Kunlik tavsiyalar obunasini yoqish/o'chirish"""
    register_user(user_id)
    conn = get_connection()
    conn.execute("UPDATE users SET daily_tips_subscribed = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def get_daily_tips_subscribers():
    """Kunlik tavsiyalarga obuna bo'lgan barcha foydalanuvchilar"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE daily_tips_subscribed = 1")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_daily_tips_status(user_id) -> int:
    """Foydalanuvchining kunlik tavsiyalar obuna holati"""
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT daily_tips_subscribed FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

# ─────────────────────────────────────────────────────────────────
# BAN TIZIMI (ADMIN BUYRUQLARI UCHUN)
# ─────────────────────────────────────────────────────────────────

def ban_user(user_id: int, duration_minutes: int = None):
    """Foydalanuvchini ban qilish. duration_minutes berilsa - vaqtinchalik, aks holda - doimiy."""
    register_user(user_id)
    conn = get_connection()
    if duration_minutes:
        banned_until = (datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)).isoformat()
        conn.execute(
            "UPDATE users SET is_banned = 1, banned_until = ? WHERE user_id = ?",
            (banned_until, user_id)
        )
    else:
        conn.execute(
            "UPDATE users SET is_banned = 1, banned_until = NULL WHERE user_id = ?",
            (user_id,)
        )
    conn.commit()
    conn.close()

def unban_user(user_id: int):
    """Foydalanuvchini bandan chiqarish."""
    register_user(user_id)
    conn = get_connection()
    conn.execute(
        "UPDATE users SET is_banned = 0, banned_until = NULL WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def is_user_banned(user_id: int) -> tuple:
    """
    Foydalanuvchi banlanganligini tekshirish.
    Qaytaradi: (is_banned: bool, message: str)
    """
    register_user(user_id)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_banned, banned_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False, ""
        
    is_banned, banned_until_str = row
    if not is_banned:
        return False, ""
        
    if banned_until_str:
        try:
            banned_until = datetime.datetime.fromisoformat(banned_until_str)
            if datetime.datetime.now() > banned_until:
                # Ban muddati tugagan — avtomatik o'chiramiz
                conn2 = get_connection()
                conn2.execute("UPDATE users SET is_banned = 0, banned_until = NULL WHERE user_id = ?", (user_id,))
                conn2.commit()
                conn2.close()
                return False, ""
            else:
                formatted_time = banned_until.strftime("%d.%m.%Y %H:%M")
                return True, f"🚫 Vaqtinchalik ban muddati: {formatted_time} gacha."
        except Exception:
            return True, "🚫 Vaqtinchalik ban faol."
            
    return True, "🚫 Doimiy (muddatsiz) ban faol."
