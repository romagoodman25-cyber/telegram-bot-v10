import requests
import time

# ===== НАСТРОЙКИ =====
API_KEY = "3f7101256f6adfdda2c7430cf15ac5d7"
TELEGRAM_TOKEN = "8472246861:AAF599zkV7yjRjeKhoiVzdlgW4e-DD1e2WI"
TELEGRAM_CHAT_ID = "ТВОЙ_ID"

old_odds_data = {}

# ===== TELEGRAM =====
def send_telegram(text):
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
data = {
"chat_id": TELEGRAM_CHAT_ID,
"text": text,
"parse_mode": "HTML"
}
requests.post(url, data=data)

# ===== API =====
def get_matches():
url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?regions=eu&markets=h2h&apiKey={API_KEY}"
res = requests.get(url)
return res.json()

# ===== V15 CORE =====
def scan():
global old_odds_data

print("🔥 V15 PRO SCAN...")

matches = get_matches()

best_bet = None
best_score = 0

for match in matches:

home = match.get("home_team")
away = match.get("away_team")

if "bookmakers" not in match:
continue

team_odds_map = {}

# ===== СОБИРАЕМ ВСЕ КЭФЫ =====
for book in match["bookmakers"]:
try:
outcomes = book["markets"][0]["outcomes"]
except:
continue

for o in outcomes:
team = o["name"]
odds = o["price"]

if team not in team_odds_map:
team_odds_map[team] = []

team_odds_map[team].append(odds)

# ===== АНАЛИЗ =====
for team, odds_list in team_odds_map.items():

if len(odds_list) < 2:
continue

max_odds = max(odds_list)
min_odds = min(odds_list)

# 📊 перекос линии (value между БК)
spread = (max_odds - min_odds) / min_odds

# 📊 вероятность
prob = 1 / max_odds
value = (prob * max_odds) - 1

# 📉 движение линии
match_key = f"{home}-{away}-{team}"
old_odds = old_odds_data.get(match_key)

sharp = False
change = 0

if old_odds:
change = (old_odds - max_odds) / old_odds

if 0.03 < change < 0.12:
sharp = True

old_odds_data[match_key] = max_odds

# 🚫 АНТИ-ПОПАН ФИЛЬТР
if max_odds < 1.6:
continue

# 🎯 СКОР СИГНАЛА
score = (spread * 2) + value + (change if sharp else 0)

if score > best_score and spread > 0.05:
best_score = score
best_bet = {
"home": home,
"away": away,
"team": team,
"odds": max_odds,
"value": round(value, 3),
"spread": round(spread * 100, 1),
"change": round(change * 100, 1),
"sharp": sharp
}

# ===== ОТПРАВКА =====
if best_bet:
sharp_text = "🔥 SHARP MONEY" if best_bet["sharp"] else "📊 LINE VALUE"

message = f"""
💎 <b>VIP SIGNAL V15</b>

{sharp_text}

⚽ {best_bet['home']} vs {best_bet['away']}

👉 <b>{best_bet['team']}</b>
Кэф: {best_bet['odds']}

📊 Value: {best_bet['value']}
📈 Перекос БК: {best_bet['spread']}%
📉 Движение: {best_bet['change']}%

💣 <b>PRO BETTING EDGE</b>
"""
send_telegram(message)
print("SEND VIP:", best_bet)

else:
print("❌ Нет VIP value")

# ===== 24/7 =====
while True:
try:
scan()
except Exception as e:
print("Ошибка:", e)

time.sleep(600)
