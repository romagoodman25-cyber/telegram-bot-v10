import requests
import time
from flask import Flask
from threading import Thread

# =====================
# НАСТРОЙКИ
# =====================
TOKEN = "ТВОЙ_ТОКЕН"
CHAT_ID = "ТВОЙ_ID"
API_KEY = "ТВОЙ_API_KEY"

# =====================
# FLASK (чтобы Render не усыпил)
# =====================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =====================
# TELEGRAM
# =====================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# =====================
# API СКАНЕР
# =====================
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    res = requests.get(url)
    
    if res.status_code != 200:
        return []
    
    return res.json()

# =====================
# ЛОГИКА VALUE
# =====================
def scan():
    matches = get_matches()
    
    if not matches:
        send_telegram("❌ Нет матчей")
        return

    best_value = 0
    best_bet = ""

    for match in matches[:5]:
        try:
            home = match["home_team"]
            away = match["away_team"]
            outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]

            for team in outcomes:
                name = team["name"]
                odd = team["price"]

                prob = 1 / odd
                value = prob * odd - 1

                if value > best_value:
                    best_value = value
                    best_bet = f"{name} | кэф {odd} | value {round(value,3)}"

        except:
            continue

    if best_bet:
        send_telegram(f"🔥 VALUE СТАВКА\n\n{best_bet}")
    else:
        send_telegram("❌ Нет value сегодня")

# =====================
# MAIN LOOP
# =====================
def main():
    keep_alive()
    
    while True:
        scan()
        time.sleep(1800)  # каждые 30 минут

if __name__ == "__main__":
    main()
