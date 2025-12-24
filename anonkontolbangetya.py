import os
import sys
import json
import base64
from datetime import datetime

# ===== COLOR SAFE =====
try:
    from termcolor import colored
except:
    def colored(t, *_a, **_k): return t

import requests
import threading
import time

# ===== CONFIG =====
ACCOUNTS_FILE = "accounts.json"
CONFIG_FILE = "config.json"
PROMPT_FILE = os.path.expanduser("~/storage/downloads/anonbreak.txt")

# ===== OWNER LOCK (BASE64) =====
_OWNER_B64 = "YW5vbmtvbnRvbGJhbmdldHN1dQ=="

def get_owner():
    return base64.b64decode(_OWNER_B64).decode()

def is_owner(u):
    return u == get_owner()

# ===== API VALIDATION =====
def api_valid(api_key):
    return (
        isinstance(api_key, str)
        and api_key.startswith("sk-or-")
        and len(api_key) > 20
    )

# ===== BANNER =====
BANNER = r"""
╔╦═╦╦═╦═╦═╦═╦══╦═╦╦═╦═╦╗
║║║║║║║╬║║║║║╔╗║║║║║║║║║
║║║║║║║╗╣║║║║╠╣║║║║║║║║║
╚═╩═╩═╩╩╩╩═╩╩╝╚╩╩═╩═╩╩═╝

WORMAN0NGPT BY AN0N
OPENROUTER AI
"""

# ===== UTIL =====
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def load_json(p, d):
    if not os.path.exists(p):
        return d
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return d

def save_json(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def pause():
    input(colored("\nTekan ENTER...", "cyan"))
    clear()

# ===== INIT FILE =====
def ensure_files():
    acc = load_json(ACCOUNTS_FILE, {})
    owner = get_owner()
    if owner not in acc:
        acc[owner] = {"expired": ""}
    save_json(ACCOUNTS_FILE, acc)

    if not os.path.exists(CONFIG_FILE):
        save_json(CONFIG_FILE, {"api_key": "", "language": "Indonesian"})

# ===== LOGIN =====
def login(acc):
    clear()
    print(colored(BANNER, "red"))
    u = input(colored("USERNAME: ", "green")).strip()

    if u not in acc:
        print(colored("[!] USERNAME TIDAK TERDAFTAR", "red"))
        sys.exit(1)

    exp = acc[u].get("expired", "")
    if exp:
        if datetime.now().date() > datetime.strptime(exp, "%Y-%m-%d").date():
            print(colored("[!] AKUN EXPIRED", "red"))
            sys.exit(1)

    clear()
    return u

# ===== PROMPT =====
def load_prompt():
    if not os.path.exists(PROMPT_FILE):
        print(colored("[!] anonbreak.txt tidak ditemukan", "red"))
        return ""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

# ===== CHAT =====
def chat(cfg):
    api_key = cfg.get("api_key", "").strip()

    if not api_valid(api_key):
        print(colored("[!] API KEY OPENROUTER BELUM DISET / TIDAK VALID", "red"))
        print(colored(">> Set dulu di menu 1", "yellow"))
        pause()
        return

    prompt = load_prompt()
    messages = []

    if prompt:
        messages.append({"role": "system", "content": prompt})

    model = "deepseek/deepseek-chat-v3-0324"
    print(colored("\n[ CHAT MODE ] ketik exit untuk kembali\n", "cyan"))

    while True:
        msg = input(colored("[AN0N] > ", "green"))
        if msg.lower() == "exit":
            clear()
            break

        messages.append({"role": "user", "content": msg})

        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages},
                timeout=60
            )

            if r.status_code != 200:
                print(colored("[!] OPENROUTER ERROR", "red"))
                print(r.text)
                break

            data = r.json()
            reply = data["choices"][0]["message"]["content"]

        except Exception as e:
            reply = f"[ERROR] {e}"

        print(colored("[WORMAN0NGPT] RESPONSE: ", "cyan") + reply)
        messages.append({"role": "assistant", "content": reply})

# ===== CREATE ACCOUNT (OWNER) =====
def create_account(acc, user):
    if not is_owner(user):
        return

    clear()
    print(colored("[ CREATE ACCOUNT ]", "cyan"))
    u = input("Username: ").strip()
    e = input("Expired (YYYY-MM-DD / kosong): ").strip()
    acc[u] = {"expired": e}
    save_json(ACCOUNTS_FILE, acc)
    print(colored("[✓] AKUN DIBUAT", "green"))
    pause()

# ===== MENU =====
def menu(user):
    acc = load_json(ACCOUNTS_FILE, {})
    cfg = load_json(CONFIG_FILE, {})

    while True:
        print(colored("\nMENU", "cyan"))
        print("1. Set API OpenRouter")
        print("2. Chat Now")
        if is_owner(user):
            print("3. Create Account (OWNER)")
        print("0. Exit")

        c = input(colored("[ AN0N ] > ", "green")).strip()

        if c == "1":
            cfg["api_key"] = input("API KEY: ").strip()
            save_json(CONFIG_FILE, cfg)
            pause()

        elif c == "2":
            clear()
            chat(cfg)

        elif c == "3" and is_owner(user):
            create_account(acc, user)

        elif c == "0":
            clear()
            sys.exit()

        else:
            clear()

# ===== BOT TELEGRAM =====
_BOT_TOKEN_B64 = "ODI5NzU3NDg4MzpBQUZJZk8yT0o0ZzdUcTd1UGxrZ3ZuaUhtM19HMkFwTFRlQQ=="
_OWNER_ID_B64 = "ODMwNDQ0MzI4Mw=="

def bot_token():
    return base64.b64decode(_BOT_TOKEN_B64).decode()

def owner_id():
    return int(base64.b64decode(_OWNER_ID_B64).decode())

BOT_API = f"https://api.telegram.org/bot{bot_token()}"
BOT_STATE = {}

def tg_send(chat_id, text):
    try:
        requests.post(f"{BOT_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)
    except: pass

def bot_loop():
    last_update = 0
    while True:
        try:
            r = requests.get(f"{BOT_API}/getUpdates", timeout=30).json()
            for u in r.get("result", []):
                uid = u["update_id"]
                if uid <= last_update:
                    continue
                last_update = uid

                msg = u.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "").strip()

                if chat_id != owner_id():
                    continue

                acc = load_json(ACCOUNTS_FILE, {})

                if text == "/createakun":
                    BOT_STATE[chat_id] = {"step": 1}
                    tg_send(chat_id, "Masukin Barang:")
                    continue

                if chat_id not in BOT_STATE:
                    continue

                state = BOT_STATE[chat_id]

                if state["step"] == 1:
                    state["barang"] = text
                    state["step"] = 2
                    tg_send(chat_id, "Masukin Username:")
                    continue

                if state["step"] == 2:
                    state["username"] = text
                    state["step"] = 3
                    tg_send(chat_id, "Masukin Expired (YYYY-MM-DD / kosong):")
                    continue

                if state["step"] == 3:
                    state["expired"] = text
                    # Save account
                    acc[state["username"]] = {"expired": state["expired"]}
                    save_json(ACCOUNTS_FILE, acc)
                    tg_send(chat_id,
                        f"HALO PAKET AKUN ANDA TELAH TIBA📩\n\n📤BARANG: {state['barang']}\n📋USERNAME: {state['username']}\n🕛WAKTU EXPIRED: {state['expired']}\n\nTERIMAKASIH SUDAH MEMBELI DI ANONSHOP\n© WORMAN0NGPT BOTZ SHOP"
                    )
                    BOT_STATE.pop(chat_id, None)
                    continue

        except:
            time.sleep(5)

# ===== MAIN =====
def main():
    ensure_files()
    acc = load_json(ACCOUNTS_FILE, {})
    user = login(acc)
    # Start bot in thread
    threading.Thread(target=bot_loop, daemon=True).start()
    menu(user)

if __name__ == "__main__":
    main()
