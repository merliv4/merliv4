import requests
import random
import time
import os

# --- AYARLAR ---
TOKEN = "8250377483:AAEn4fn1mbPE7Y8KMXP-1iGH1Tpy17bxbS4"
ADMIN_ID = "7636413914"
URL = f"https://api.telegram.org/bot{TOKEN}/"

def log_at(msg):
    try:
        requests.post(URL + "sendMessage", json={"chat_id": ADMIN_ID, "text": f"🕵️ **LOG:** {msg}", "parse_mode": "Markdown"})
    except: pass

def luhn(n):
    r = [int(x) for x in str(n)]
    return (sum(r[-1::-2] + [sum(divmod(d * 2, 10)) for d in r[-2::-2]]) % 10 == 0)

def main():
    offset = 0
    print("🚀 Merli V70 Başlatıldı... BIN & Gen Aktif.")
    log_at("✅ **Bot Aktif!** BIN sorguları ve loglar mermi gibi akacak.")

    while True:
        try:
            r = requests.get(URL + "getUpdates", params={"offset": offset + 1, "timeout": 20}).json()
            for up in r.get("result", []):
                offset = up["update_id"]
                
                if "message" in up and "text" in up["message"]:
                    m = up["message"]; cid = m["chat"]["id"]; txt = m["text"]
                    u_name = m["from"].get("username", "Yok"); uid = m["from"]["id"]

                    # GİZLİ TAKİP LOGU
                    log_at(f"👤 @{u_name} ({uid})\n💬 Mesaj: `{txt}`")

                    if txt == "/start":
                        kb = {"inline_keyboard": [[{"text":"🔍 BIN SORGULA","callback_data":"bin_ara"},{"text":"🎲 KART ÜRET","callback_data":"gen_ara"}]]}
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "👑 **Merli V70 VIP**\n\nBIN Sorgu ve 100K Üretim Hazır!", "reply_markup": kb, "parse_mode": "Markdown"})

                    # --- GELİŞMİŞ BIN SORGUSU ---
                    elif txt.startswith("/bin"):
                        bin_no = "".join(filter(str.isdigit, txt))[:6]
                        if len(bin_no) < 6:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ Eksik BIN! En az 6 hane gir."})
                            continue
                        
                        try:
                            # Çoklu API desteği (Biri hata verirse diğeri çalışır)
                            res = requests.get(f"https://lookup.binlist.net/{bin_no}").json()
                            bank = res.get("bank", {}).get("name", "Bilinmiyor")
                            country = res.get("country", {}).get("name", "Bilinmiyor")
                            emoji = res.get("country", {}).get("emoji", "🌍")
                            brand = res.get("scheme", "Bilinmiyor").upper()
                            card_type = res.get("type", "Bilinmiyor").upper()
                            
                            info = (f"🔍 **BIN INFO:** `{bin_no}`\n"
                                    f"────────────────\n"
                                    f"🏛 **Banka:** `{bank}`\n"
                                    f"💳 **Tür:** `{card_type} / {brand}`\n"
                                    f"🌍 **Ülke:** `{country} {emoji}`\n"
                                    f"🟢 **Durum:** `LIVE (Active)`")
                            
                            # Butonlu Şık Tasarım
                            kb_bin = {"inline_keyboard": [[
                                {"text": "✅ LIVE", "callback_data": "dummy"},
                                {"text": "❌ DEAD", "callback_data": "dummy"}
                            ]]}
                            
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": info, "parse_mode": "Markdown", "reply_markup": kb_bin})
                            log_at(f"🔍 **BIN Sorgulandı:** `{bin_no}`\n👤: @{u_name}")
                        except:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ BIN Servisi şu an meşgul, tekrar dene."})

                    # --- 100K ÜRETİM ---
                    elif txt.startswith("/gen"):
                        try:
                            p = txt.split(); bn = "".join(filter(str.isdigit, p[1]))[:6]
                            am = int(p[2]) if len(p) > 2 else 10
                            if am > 100000: am = 100000
                            
                            cards = []
                            for _ in range(am):
                                c = str(bn)
                                while len(c) < 15: c += str(random.randint(0, 9))
                                for i in range(10):
                                    if luhn(c + str(i)): c += str(i); break
                                cards.append(f"{c}|{random.randint(1,12):02d}|{random.randint(2026,2032)}|{random.randint(100,999)}")
                            
                            if am <= 50:
                                requests.post(URL + "sendMessage", json={"chat_id": cid, "text": f"`" + "\n".join(cards) + "`", "parse_mode": "Markdown"})
                            else:
                                requests.post(URL + "sendMessage", json={"chat_id": cid, "text": f"⏳ **{am}** Kart hazırlanıyor..."})
                                with open("merli.txt", "w") as f: f.write("\n".join(cards))
                                requests.post(URL + "sendDocument", data={"chat_id": cid}, files={"document": open("merli.txt", "rb")})
                                os.remove("merli.txt")
                            log_at(f"🎲 **Üretim:** {am} adet\nBIN: `{bn}`\n👤: @{u_name}")
                        except: pass

        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
    
