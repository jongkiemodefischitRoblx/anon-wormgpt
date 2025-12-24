import os, sys, json, base64, requests
from datetime import datetime

# ================= FILE =================
ACCOUNTS_FILE = "accounts.json"
CONFIG_FILE = "config.json"
PROMPT_FILE = "anonbreak.txt"

# ================= OWNER (BASE64) =================
_OWNER_B64 = "YW5vbmtvbnRvbGJhbmdldHlh"

def owner_name():
    return base64.b64decode(_OWNER_B64).decode()

def is_owner(u):
    return u == owner_name()

# ================= UTIL =================
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def load_json(p, d):
    if not os.path.exists(p):
        return d
    try:
        return json.load(open(p, "r", encoding="utf-8"))
    except:
        return d

def save_json(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), indent=2)

def pause():
    input("\nENTER...")
    clear()

# ================= INIT =================
def init_files():
    if not os.path.exists(ACCOUNTS_FILE):
        save_json(ACCOUNTS_FILE, {
            owner_name(): {"expired": ""}
        })

    if not os.path.exists(CONFIG_FILE):
        save_json(CONFIG_FILE, {"api_key": ""})

# ================= LOGIN =================
def login():
    clear()
    acc = load_json(ACCOUNTS_FILE, {})
    u = input("USERNAME: ").strip()

    if u not in acc:
        print("[!] USERNAME TIDAK TERDAFTAR")
        sys.exit(1)

    exp = acc[u]["expired"]
    if exp:
        if datetime.now().date() > datetime.strptime(exp, "%Y-%m-%d").date():
            print("\nAKUN LU UDAH EXPIRED\nBEGO BELI LAGI SONO\n")
            sys.exit(1)

    return u

# ================= PROMPT =================
def load_prompt():
    if not os.path.exists(PROMPT_FILE):
        return ""
    return open(PROMPT_FILE, "r", encoding="utf-8").read()

# ================= CHAT =================
def chat():
    cfg = load_json(CONFIG_FILE, {})
    api = cfg.get("api_key", "").strip()

    if not api.startswith("sk-or-"):
        print("[!] API OPENROUTER BELUM DISET")
        pause()
        return

    messages = []
    prompt = load_prompt()
    if prompt:
        messages.append({"role": "system", "content": prompt})

    print("\n[ CHAT MODE ] ketik exit untuk keluar\n")

    while True:
        q = input("[AN0N] > ")
        if q.lower() == "exit":
            clear()
            return

        messages.append({"role": "user", "content": q})

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": messages
            }
        )

        res = r.json()["choices"][0]["message"]["content"]
        print("\n[AI]:", res, "\n")
        messages.append({"role": "assistant", "content": res})

# ================= CREATE ACCOUNT (OWNER) =================
def create_account():
    acc = load_json(ACCOUNTS_FILE, {})
    clear()

    user = input("Username: ").strip()
    exp = input("Expired (YYYY-MM-DD): ").strip()

    acc[user] = {"expired": exp}
    save_json(ACCOUNTS_FILE, acc)

    clear()
    print("HALO PAKET ANDA TELAH TIBA:")
    print(f"BARANG: WORMAN0NGPT AKUN")
    print(f"USERNAME: {user}")
    print(f"EXPIRED: {exp}")
    pause()

# ================= MENU =================
def menu(user):
    while True:
        print("\nMENU")

        if is_owner(user):
            print("1. Create Akun")
            print("2. Set Api Openrouter")
            print("3. Start Chat")
            print("4. Exit")
        else:
            print("1. Set Api Openrouter")
            print("2. Start Chat")
            print("3. Exit")

        c = input("[ AN0N ] > ").strip()

        if is_owner(user):
            if c == "1":
                create_account()
            elif c == "2":
                cfg = load_json(CONFIG_FILE, {})
                cfg["api_key"] = input("API KEY: ").strip()
                save_json(CONFIG_FILE, cfg)
                pause()
            elif c == "3":
                chat()
            elif c == "4":
                sys.exit()
        else:
            if c == "1":
                cfg = load_json(CONFIG_FILE, {})
                cfg["api_key"] = input("API KEY: ").strip()
                save_json(CONFIG_FILE, cfg)
                pause()
            elif c == "2":
                chat()
            elif c == "3":
                sys.exit()

        clear()

# ================= MAIN =================
def main():
    init_files()
    user = login()
    menu(user)

if __name__ == "__main__":
    main()
