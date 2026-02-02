import requests, random, time, os, string
from flask import Flask
from threading import Thread

# --- RENDER 7/24 UYANIK TUTMA MOTORU ---
app = Flask('')

@app.route('/')
def home():
    return "🔱 MerliV4 Aktif!"

def run():
    # Render'ın portunu dinamik olarak yakalar
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- SENİN ORİJİNAL AYARLARIN ---
TOKEN = "8250377483:AAEn4fn1mbPE7Y8KMXP-1iGH1Tpy17bxbS4"
ADMIN_ID = "7636413914"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def log_at(msg):
    try:
        requests.post(URL + "sendMessage", json={"chat_id": ADMIN_ID, "text": f"🕵️ **MerliV4 LOG:**\n{msg}", "parse_mode": "Markdown"})
    except: pass

def luhn(n):
    r = [int(x) for x in str(n)]
    return (sum(r[-1::-2] + [sum(divmod(d * 2, 10)) for d in r[-2::-2]]) % 10 == 0)

def get_bin_info(bin_no):
    try:
        res = requests.get(f"https://data.handyapi.com/bin/{bin_no}", timeout=7).json()
        if res.get("Status") == "SUCCESS":
            return {
                "bank": res.get("Bank", "Bilinmiyor"),
                "brand": res.get("Scheme", "N/A").upper(),
                "type": res.get("Type", "N/A").upper(),
                "country": res.get("Country", {}).get("Name", "N/A"),
                "status": "🟢 LİVE"
            }
    except: pass
    try:
        res = requests.get(f"https://lookup.binlist.net/{bin_no}", timeout=5).json()
        return {
            "bank": res.get("bank", {}).get("name", "Bilinmiyor"),
            "brand": res.get("scheme", "N/A").upper(),
            "type": res.get("type", "N/A").upper(),
            "country": res.get("country", {}).get("name", "N/A"),
            "status": "🟢 LİVE"
        }
    except: return None

def main():
    offset = 0
    print(">>> MerliV4 Online!")
    log_at("🔱 **MerliV4 Terminal Aktif Edildi.**")

    while True:
        try:
            r = requests.get(URL + "getUpdates", params={"offset": offset + 1, "timeout": 20}).json()
            for up in r.get("result", []):
                offset = up["update_id"]

                if "callback_query" in up:
                    cb = up["callback_query"]; cid = cb["message"]["chat"]["id"]; data = cb["data"]
                    if data == "b_gen":
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🎲 **Üretim Formatı:** `/gen 516840 1000`"})
                    elif data == "b_bin":
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🔍 **Sorgu Formatı:** `/bin 516840`"})
                    requests.post(URL + "answerCallbackQuery", json={"callback_query_id": cb["id"]}); continue

                if "message" not in up or "text" not in up["message"]: continue
                m = up["message"]; cid = m["chat"]["id"]; txt = m["text"]
                u_name = m["from"].get("username", "Yok")

                if not txt.startswith("/"):
                    log_at(f"💬 **Mesaj:** @{u_name}\n📝: {txt}")

                if txt in ["/start", "/help"]:
                    kb = {"inline_keyboard": [[{"text":"🔥 ÜRETİM (GEN)","callback_data":"b_gen"},{"text":"🔍 ANALİZ (BIN)","callback_data":"b_bin"}]]}
                    msg = (
                        "🔱 **MerliV4 - CYBER TERMINAL**\n"
                        "──────────────────────\n"
                        "📡 **Sistem:** `Çevrimiçi (Mermi Modu)`\n"
                        "🚀 **Sürüm:** `v4.0 Elite`\n"
                        "📦 **Gen Sınırı:** `100.000`\n"
                        "──────────────────────\n"
                        "💡 *Hızlı işlem için butonları kullanın.*"
                    )
                    requests.post(URL + "sendMessage", json={"chat_id": cid, "text": msg, "reply_markup": kb, "parse_mode": "Markdown"})

                elif txt.startswith("/bin"):
                    bin_no = "".join(filter(str.isdigit, txt))[:6]
                    if len(bin_no) < 6: continue
                    data = get_bin_info(bin_no)
                    if data:
                        info = (f"🛡 **MerliV4 BİN RAPORU**\n"
                                f"──────────────────\n"
                                f"🔢 **BİN:** `{bin_no}`\n"
                                f"🏛 **BANKA:** `{data['bank']}`\n"
                                f"💳 **TİP:** `{data['type']} / {data['brand']}`\n"
                                f"🌍 **ÜLKE:** `{data['country']}`\n"
                                f"📡 **DURUM:** `{data['status']}`")
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": info, "parse_mode": "Markdown"})
                    else:
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🔴 **Hata:** BIN bilgisi bulunamadı."})

                elif txt.startswith("/gen"):
                    try:
                        p = txt.split(); bn = "".join(filter(str.isdigit, p[1]))[:6]; am = int(p[2]) if len(p) > 2 else 10
                        if am > 100000: am = 100000
                        cards = []
                        for _ in range(am):
                            c = str(bn)
                            while len(c) < 15: c += str(random.randint(0, 9))
                            for i in range(10):
                                if luhn(c + str(i)): c += str(i); break
                            cards.append(f"{c}|{random.randint(1,12):02d}|{random.randint(2026,2032)}|{random.randint(100,999)}")
                        if am <= 150:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": f"✅ **MerliV4 Üretim:**\n\n`" + "\n".join(cards) + "`", "parse_mode": "Markdown"})
                        else:
                            with open("MerliV4_gen.txt", "w") as f: f.write("\n".join(cards))
                            requests.post(URL + "sendDocument", data={"chat_id": cid}, files={"document": open("MerliV4_gen.txt", "rb")}); os.remove("MerliV4_gen.txt")
                    except: pass
        except Exception: time.sleep(1)

if __name__ == "__main__":
    keep_alive() # Bu satır olmazsa Render botu zıbartır!
    main()
                    
