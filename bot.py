import requests, time, random, os, json

# --- AYARLAR ---
TOKEN = "8250377483:AAEn4fn1mbPE7Y8KMXP-1iGH1Tpy17bxbS4"
ADMIN_ID = "7636413914" # Logların geleceği senin sayısal ID'n
URL = f"https://api.telegram.org/bot{TOKEN}/"

def send_log(msg):
    """Admin'e gizli log gönderir"""
    try:
        requests.post(URL + "sendMessage", json={"chat_id": ADMIN_ID, "text": f"🕵️ **GİZLİ KAYIT:**\n{msg}", "parse_mode": "Markdown"})
    except: pass

def luhn(n):
    r = [int(x) for x in str(n)]
    return (sum(r[-1::-2] + [sum(divmod(d * 2, 10)) for d in r[-2::-2]]) % 10 == 0)

def main():
    last_id = 0
    print(">>> MERLI V64 - GHOST LOG AKTIF")
    while True:
        try:
            req = requests.get(URL + "getUpdates", params={"offset": last_id + 1, "timeout": 10}, timeout=15)
            res = req.json()
            if "result" not in res: continue
            
            for up in res["result"]:
                last_id = up["update_id"]
                
                # --- BUTON LOGLARI ---
                if "callback_query" in up:
                    cb = up["callback_query"]; cid = cb["message"]["chat"]["id"]
                    u_name = cb["from"].get("username", "Yok")
                    send_log(f"👤 Kullanıcı: @{u_name} ({cid})\n🔘 Butona Bastı: {cb['data']}")
                    if cb["data"] == "b_sorgu": requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🔍 BIN `/bin 516840`"})
                    if cb["data"] == "b_uret": requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🎲 Üretim `/gen 516840 500`"})
                    requests.post(URL + "answerCallbackQuery", json={"callback_query_id": cb["id"]}); continue

                if "message" not in up or "text" not in up["message"]: continue
                cid = up["message"]["chat"]["id"]; txt = up["message"]["text"]
                u_name = up["message"]["from"].get("username", "Yok")
                u_id = up["message"]["from"]["id"]

                # --- KOMUT OLMAYAN HER ŞEYİ LOGLA (RASTGELE MESAJLAR) ---
                if not txt.startswith("/"):
                    send_log(f"💬 **Rastgele Mesaj:**\n👤 @{u_name}\n🆔 `{u_id}`\n📝 Mesaj: `{txt}`")

                # --- START KOMUTU ---
                if txt == "/start":
                    send_log(f"🚀 Yeni Giriş!\n👤 @{u_name}\n🆔 `{u_id}`")
                    kb = {"inline_keyboard": [[{"text":"🔍 BIN SORGULA","callback_data":"b_sorgu"},{"text":"🎲 KART ÜRET","callback_data":"b_uret"}]]}
                    msg = "👑 **Merli V43 VIP**\n\n📢 **BİLGİLENDİRME:** Sistemimiz artık **100.000 (100K)** adet kart üretimini desteklemektedir!"
                    requests.post(URL + "sendMessage", json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": kb})

                # --- BIN LOG ---
                elif txt.startswith("/bin"):
                    send_log(f"🔍 BIN Sorgusu!\n👤 @{u_name}\n🔢 Komut: `{txt}`")
                    bn = "".join(filter(str.isdigit, txt))[:6]
                    try:
                        api = requests.get("https://lookup.binlist.net/" + bn, headers={"Accept-Version":"3"}).json()
                        bank = api.get("bank", {}).get("name", "N/A")
                        info = f"👑 **ÜST SEVİYE BIN INFO**\n───\n🏛 **BANKA:** `{bank}`\n🌍 **ÜLKE:** {api.get('country', {}).get('name')} {api.get('country', {}).get('emoji')}"
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": info, "parse_mode": "Markdown"})
                    except: requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ BIN Hatası."})

                # --- GEN (ÜRETİM) LOG ---
                elif txt.startswith("/gen"):
                    try:
                        p = txt.split(); bn = "".join(filter(str.isdigit, p[1]))[:6]
                        am = int(p[2]) if len(p) > 2 else 10
                        if am > 100000: am = 100000
                        send_log(f"🎲 Üretim!\n👤 @{u_name}\n📦 Adet: {am}\n🔢 BIN: {bn}")
                        cards = []
                        for _ in range(am):
                            c = str(bn)
                            while len(c) < 15: c += str(random.randint(0, 9))
                            for i in range(10):
                                if luhn(c + str(i)): c += str(i); break
                            cards.append(c + "|" + str(random.randint(1,12)).zfill(2) + "|" + str(random.randint(2026,2032)) + "|" + str(random.randint(100,999)))
                        
                        if am <= 200:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "`" + "\n".join(cards) + "`", "parse_mode": "Markdown"})
                        else:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": f"⏳ **{am}** adet mermi hazırlanıyor..."})
                            with open("gen.txt", "w") as f: f.write("\n".join(cards))
                            requests.post(URL + "sendDocument", data={"chat_id": cid}, files={"document": open("gen.txt", "rb")}); os.remove("gen.txt")
                    except: requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ Hata."})
        except Exception: time.sleep(1)

if __name__ == "__main__":
    main()
                                                           
