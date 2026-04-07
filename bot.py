import requests
import time

# === НАСТРОЙКИ ===
API_KEY = "3f7101256f6adfdda2c7430cf15ac5d7"
BOT_TOKEN = "8472246861:AAF599zkV7yjRjeKhoiVzdlgW4e-DD1e2WI"
CHAT_ID = 8437661219

# === ФУНКЦИЯ ОТПРАВКИ В ТГ ===
def send_telegram(text):
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
"chat_id": CHAT_ID,
"text": text
}
requests.post(url, data=data)

# === ПОЛУЧЕНИЕ МАТЧЕЙ ===
def get_matches():
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
res = requests.get(url)
return res.json()

# === РАСЧЕТ VALUE (УЛУЧШЕННЫЙ) ===
def calculate_value(prob, odds):
return (prob * odds) - 1

# === УМНАЯ МОДЕЛЬ V16 ===
def smart_model(home_odds, away_odds):
# базовая вероятность
home_prob = 1 / home_odds
away_prob = 1 / away_odds

# нормализация
total = home_prob + away_prob
home_prob /= total
away_prob /= total

# === V16 УЛУЧШЕНИЯ ===

# фаворит не всегда выгоден → штраф
if home_odds < 1.8:
home_prob *= 0.95

if away_odds < 1.8:
away_prob *= 0.95

# андердог value буст
if home_odds > 3:
home_prob *= 1.1

if away_odds > 3:
away_prob *= 1.1

return home_prob, away_prob

# === ФИЛЬТР ПРОФИ СТАВОК ===
def is_pro_bet(value, odds):
if value < 0.15:
return False

if odds < 1.5:
return False

if odds > 6:
return False

return True

# === ОСНОВНОЙ СКАНЕР ===
def scan():
print("🔍 V16 SCAN...")

matches = get_matches()

best_bet = None
best_value = 0

for match in matches:
try:
home = match["home_team"]
away = match["away_team"]

outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]

home_odds = None
away_odds = None

for o in outcomes:
if o["name"] == home:
home_odds = o["price"]
elif o["name"] == away:
away_odds = o["price"]

if not home_odds or not away_odds:
continue

home_prob, away_prob = smart_model(home_odds, away_odds)

home_value = calculate_value(home_prob, home_odds)
away_value = calculate_value(away_prob, away_odds)

# === ФИЛЬТР V16 ===
if is_pro_bet(home_value, home_odds):
if home_value > best_value:
best_value = home_value
best_bet = (home, home_odds, home_value)

if is_pro_bet(away_value, away_odds):
if away_value > best_value:
best_value = away_value
best_bet = (away, away_odds, away_value)

except:
continue

# === РЕЗУЛЬТАТ ===
if best_bet:
team, odds, value = best_bet

msg = f"""🔥 V16 PRO SIGNAL

👉 {team}
Кэф: {round(odds, 2)}
Value: {round(value, 3)}

📊 Фильтр: PRO + Антипопан + Value"""

print(msg)
send_telegram(msg)

else:
msg = "❌ V16: Нет value сегодня"
print(msg)
send_telegram(msg)

# === БЕСКОНЕЧНЫЙ ЗАПУСК ===
while True:
scan()
time.sleep(900) # каждые 15 минут
