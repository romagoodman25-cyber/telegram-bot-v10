# 🔐 ТВОИ ДАННЫЕ
BOT_TOKEN = "8472246861:AAF599zkV7yjRjeKhoiVzdlgW4e-DD1e2WI"
CHAT_ID = 8437661219

# 📩 ОТПРАВКА В TELEGRAM
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    
    requests.post(url, json=payload)


# 📊 ГЕНЕРАЦИЯ СИГНАЛА (V16)
def generate_signal():
    direction = random.choice(["BUY 📈", "SELL 📉"])
    value = random.randint(70, 95)  # сила сигнала
    return f"🔥 SIGNAL V16 PRO\n\nDirection: {direction}\nStrength: {value}%"


# 🚀 ОСНОВНОЙ ЦИКЛ
def main():
    send_telegram_message("🤖 BOT V16 STARTED")

    while True:
        signal = generate_signal()
        send_telegram_message(signal)
        time.sleep(60)  # каждые 60 секунд


# ▶️ ЗАПУСК
if __name__ == "__main__":
    main()
