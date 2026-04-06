import requests
import time

# =========================
# 🔑 ВСТАВЬ СЮДА СВОИ ДАННЫЕ
# =========================
BOT_TOKEN = "8472246861:AAF599zkV7yjRjeKhoiVzdlgW4e-DD1e2WI"
CHAT_ID = 8437661219

# API ключ (The Odds API)
API_KEY = "ТУТ_API_KEY"

# =========================

def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/"
    
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print("Ошибка API")
        return []

    return response.json()


def find_value_bets(matches):
    best_bet = None
    best_value = 0

    for match in matches:
        try:
            teams = match["teams"]
            odds = match["bookmakers"][0]["markets"][0]["outcomes"]

            for team in odds:
                name = team["name"]
                odd = team["price"]

                # простая модель (можно апгрейдить потом)
                probability = 1 / odd
                value = probability * odd - 1

                if value > best_value:
                    best_value = value
                    best_bet = (name, odd, value)

        except:
            continue

    return best_bet


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


def run_bot():
    print("🚀 Бот запущен...")

    while True:
        matches = get_matches()

        if matches:
            bet = find_value_bets(matches)

            if bet:
                team, odd, value = bet

                message = f"""🔥 V10 LIVE VALUE

👉 {team}
Кэф: {odd}
Value: {round(value, 3)}"""

                print(message)
                send_telegram(message)

        else:
            print("Нет матчей")

        time.sleep(600)  # каждые 10 минут


if __name__ == "__main__":
    run_bot()
