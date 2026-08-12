import os
import sys
import time
import subprocess
import re
import signal
import socket

# Rangli matnlar uchun
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

print(f"{colors.HEADER}{colors.BOLD}🚀 Birinchi Yordam Bot & Mini App - Avtomatik Ishga Tushirish{colors.ENDC}\n")

processes = []

def cleanup(sig=None, frame=None):
    print(f"\n{colors.WARNING}🛑 Jarayonlar to'xtatilmoqda...{colors.ENDC}")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print(f"{colors.GREEN}✅ Barcha jarayonlar to'xtatildi! Xayr!{colors.ENDC}")
    sys.exit(0)

# Ctrl+C bosilganda tozalash
signal.signal(signal.SIGINT, cleanup)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

try:
    # 1. Portni tekshiramiz va Python veb-serverini ishga tushiramiz (port: 8000)
    print(f"{colors.BLUE}1. Veb-server porti tekshirilmoqda...{colors.ENDC}")
    if is_port_in_use(8000):
        print(f"{colors.WARNING}⚠️ Diqqat: Port 8000 allaqachon band!{colors.ENDC}")
        print(f"{colors.WARNING}Fonda eski python server yoki boshqa dastur ishlayotgan bo'lishi mumkin.{colors.ENDC}")
        print(f"{colors.WARNING}Agar hozir ishlamasa, kompyuterni qayta yuklang yoki fondagi python.exe jarayonlarini yoping.{colors.ENDC}\n")
    
    print(f"{colors.BLUE}Veb-server ishga tushirilmoqda (127.0.0.1:8000)...{colors.ENDC}")
    app_dir = os.path.join(os.path.dirname(__file__), "app")
    web_server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=app_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(web_server)
    time.sleep(1.5)

    # Veb-server xatolikka uchraganini tekshirish
    if web_server.poll() is not None:
        error_output = web_server.stderr.read()
        print(f"{colors.FAIL}❌ Veb-server ishga tushmadi! Xatolik:{colors.ENDC}")
        print(error_output)
        cleanup()

    # 2. Cloudflare tunnelini ishga tushirib, havolani o'qiymiz
    print(f"{colors.BLUE}2. Cloudflare tunneli yoqilmoqda (havola olinmoqda)...{colors.ENDC}")
    # Windowsda localhost o'rniga 127.0.0.1 ishlatamiz (IPv6 muammosini oldini olish uchun)
    tunnel = subprocess.Popen(
        ["npx", "-y", "cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )
    processes.append(tunnel)

    # Havolani aniqlash (re orqali .trycloudflare.com ni qidiramiz)
    mini_app_url = None
    start_time = time.time()
    
    while True:
        if time.time() - start_time > 30: # 30 soniya kutish
            print(f"{colors.FAIL}❌ Cloudflare havolasini olib bo'lmadi (vaqt tugadi).{colors.ENDC}")
            cleanup()
            
        line = tunnel.stdout.readline()
        if not line:
            break
            
        # Havolani qidirish
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            mini_app_url = match.group(0)
            print(f"{colors.GREEN}✅ Yangi havola olindi: {colors.BOLD}{mini_app_url}{colors.ENDC}")
            break

    if not mini_app_url:
        print(f"{colors.FAIL}❌ Havola topilmadi.{colors.ENDC}")
        cleanup()

    # 3. .env faylini avtomatik yangilash
    print(f"{colors.BLUE}3. .env fayliga yangi havola yozilmoqda...{colors.ENDC}")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # MINI_APP_URL qatorini topib almashtiramiz yoki qo'shamiz
        if "MINI_APP_URL=" in content:
            content = re.sub(r'MINI_APP_URL=.*', f'MINI_APP_URL={mini_app_url}', content)
        else:
            content += f"\nMINI_APP_URL={mini_app_url}\n"
            
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{colors.GREEN}✅ .env fayli muvaffaqiyatli yangilandi!{colors.ENDC}")
    else:
        print(f"{colors.WARNING}⚠️ .env fayli topilmadi.{colors.ENDC}")

    # 4. Telegram botni ishga tushiramiz
    print(f"{colors.BLUE}4. Telegram bot ishga tushirilmoqda...{colors.ENDC}")
    print(f"{colors.WARNING}💡 Chiqish va o'chirish uchun istalgan vaqt Ctrl + C tugmasini bosing.{colors.ENDC}\n")
    
    bot_process = subprocess.Popen([sys.executable, "bot.py"])
    processes.append(bot_process)
    
    # Bot tugaguncha kutib turamiz
    bot_process.wait()

except KeyboardInterrupt:
    cleanup()
except Exception as e:
    print(f"{colors.FAIL}❌ Kutilmagan xatolik: {e}{colors.ENDC}")
    cleanup()
