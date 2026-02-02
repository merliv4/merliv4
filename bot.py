import requests, time, random, os, json

TOKEN = "8250377483:AAEn4fn1mbPE7Y8KMXP-1iGH1Tpy17bxbS4"
URL = "https://api.telegram.org/bot" + TOKEN + "/"

def luhn(n):
    r = [int(x) for x in str(n)]
    return (sum(r[-1::-2] + [sum(divmod(d * 2, 10)) for d in r[-2::-2]]) % 10 == 0)

def main():
    last_id = 0
    print(">>> SISTEM ONLINE - MERLI V62")
    while True:
        try:
            req = requests.get(URL + "getUpdates", params={"offset": last_id + 1, "timeout": 10}, timeout=15)
            res = req.json()
            if "result" not in res: continue
            
            for up in res["result"]:
                last_id = up["update_id"]
                
                # --- BUTON TIKLAMALARI ---
                if "callback_query" in up:
                    cb = up["callback_query"]; cid = cb["message"]["chat"]["id"]
                    if cb["data"] == "b_sorgu": requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🔍 BIN Sorgusu için `/bin 516840` yazın."})
                    if cb["data"] == "b_uret": requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "🎲 Üretim için `/gen 516840 500` yazın."})
                    requests.post(URL + "answerCallbackQuery", json={"callback_query_id": cb["id"]}); continue

                # --- MESAJ KONTROL ---
                if "message" not in up or "text" not in up["message"]: continue
                cid = up["message"]["chat"]["id"]; txt = up["message"]["text"]
                
                # --- START KOMUTU ---
                if txt == "/start":
                    kb = {"inline_keyboard": [[{"text":"🔍 BIN SORGULA","callback_data":"b_sorgu"},{"text":"🎲 KART ÜRET","callback_data":"b_uret"}]]}
                    msg = "📢 **BİLGİLENDİRME:** Sistemimiz artık **100.000 (100K)** adet kart üretimini desteklemektedir!\n\n👑 **Merli V43 VIP**\n\nİşlem yapmak için aşağıdaki butonları kullanabilir veya komutları yazabilirsin."
                    requests.post(URL + "sendMessage", json={"chat_id": cid, "text": msg, "parse_mode": "Markdown", "reply_markup": kb})

                # --- BIN SORGULAMA ---
                elif txt.startswith("/bin"):
                    bn = "".join(filter(str.isdigit, txt))[:6]
                    try:
                        api = requests.get("https://lookup.binlist.net/" + bn, headers={"Accept-Version":"3"}).json()
                        bank = api.get("bank", {}).get("name", "N/A")
                        cntry = api.get("country", {}).get("name", "N/A")
                        flag = api.get("country", {}).get("emoji", "🌍")
                        info = f"👑 **ÜST SEVİYE BIN INFO**\n───\n🏛 **BANKA:** `{bank}`\n🌍 **ÜLKE:** {cntry} {flag}\n💳 **TİP:** {api.get('scheme')} - {api.get('type')}\n💎 **MARKA:** {api.get('brand')}"
                        requests.post(URL + "sendMessage", json={"chat_id": cid, "text": info, "parse_mode": "Markdown"})
                    except: requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ BIN Hatası / Bulunamadı."})

                # --- KART ÜRETİM (100K DESTEKLİ) ---
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
                            cards.append(c + "|" + str(random.randint(1,12)).zfill(2) + "|" + str(random.randint(2026,2032)) + "|" + str(random.randint(100,999)))
                        
                        if am <= 200:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "`" + "\n".join(cards) + "`", "parse_mode": "Markdown"})
                        else:
                            requests.post(URL + "sendMessage", json={"chat_id": cid, "text": f"⏳ **{am}** adet mermi hazırlanıyor, dosya geliyor..."})
                            with open("gen.txt", "w") as f: f.write("\n".join(cards))
                            requests.post(URL + "sendDocument", data={"chat_id": cid}, files={"document": open("gen.txt", "rb")}); os.remove("gen.txt")
                    except: requests.post(URL + "sendMessage", json={"chat_id": cid, "text": "❌ Kullanım: `/gen 516840 500`"})
        
        except Exception: time.sleep(1)

if __name__ == "__main__":
    main()
