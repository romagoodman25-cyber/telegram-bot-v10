import requests
import time
import threading
from flask import Flask

# ==============================
# 🔑 НАСТРОЙКИ (ВСТАВЬ СВОИ)
# ==============================

API_KEY = "3f7101256f6adfdda2c7430cf15ac5d7"
TELEGRAM_TOKEN = "8472246861:AAF599zkV7yjRjeKhoiVzdlgW4e-DD1e2WI"
CHAT_ID = 8437661219

# ==============================
# 📡 TELEGRAM
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=data)
    except:
        print("Ошибка отправки в Telegram")

# ==============================
# 📊 ПОЛУЧЕНИЕ МАТЧЕЙ (API)
# ==============================

def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except:
        print("Ошибка API")
        return []

# ==============================
# 🧠 МОДЕЛЬ (ELITE V10)
# ==============================

def calculate_value(prob, odds):
    return (prob * odds) - 1

def analyze_match(match):
    try:
        teams = match["teams"]
        home = match["home_team"]

        outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]

        odds_home = 0
        odds_away = 0

        for o in outcomes:
            if o["name"] == teams[0]:
                odds_home = o["price"]
            else:
                odds_away = o["price"]

        # 🔥 УМНАЯ МОДЕЛЬ (без рандома)
        base_home = 0.5
        base_away = 0.5

        # домашний фактор
        if home == teams[0]:
            base_home += 0.05
            base_away -= 0.05
        else:
            base_home -= 0.05
            base_away += 0.05

        # нормализация
        total = base_home + base_away
        prob_home = base_home / total
        prob_away = base_away / total

        value_home = calculate_value(prob_home, odds_home)
        value_away = calculate_value(prob_away, odds_away)

        return {
            "match": f"{teams[0]} vs {teams[1]}",
            "home": (teams[0], prob_home, odds_home, value_home),
            "away": (teams[1], prob_away, odds_away, value_away)
        }

    except:
        return None

# ==============================
# 🔍 СКАНЕР
# ==============================

def scan():
    print("🔍 LIVE SCAN...")

    matches = get_matches()

    if not matches:
        print("❌ Нет матчей")
        return

    best_bet = None

    for match in matches:
        result = analyze_match(match)

        if not result:
            continue

        print("\n==============================")
        print(result["match"])

        for side in ["home", "away"]:
            team, prob, odds, value = result[side]

            print(f"{team}: {round(prob*100,1)}% | кэф {odds} | value {round(value,3)}")

            if value > 0.05:
                if not best_bet or value > best_bet["value"]:
                    best_bet = {
                        "team": team,
                        "odds": odds,
                        "value": value
                    }

    if best_bet:
        message = f"🔥 LIVE СТАВКА\n\n{best_bet['team']}\nКэф: {best_bet['odds']}\nValue: {round(best_bet['value'],3)}"
        send_telegram(message)

    else:
        print("❌ Нет value")

# ==============================
# 🔁 ЦИКЛ 24/7
# ==============================

def run_bot():
    while True:
        scan()
        time.sleep(600)  # каждые 10 минут

# ==============================
# 🌐 WEB (для Render)
# ==============================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ==============================
# 🚀 ЗАПУСК
# ==============================

threading.Thread(target=run_bot).start()
run_web()
