import json
import os
from flask import Flask, request
from collections import Counter
from telegram import Bot, Update

TOKEN = os.getenv("6356929835:AAGVIHodQ_17B0a2iCd_Uk5nNhF9M3C81Pc")  # Токен лучше хранить в переменных окружения
bot = Bot(token=TOKEN)

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    if update.message:
        text = update.message.text
        chat_id = update.message.chat_id

        if text == "/start":
            bot.send_message(chat_id, "🚀 Бот работает (Webhook). Отправляй числа от 1 до 37.")
            return "ok"

        if text == "/predict":
            data = load_data()
            if len(data) < 20:
                bot.send_message(chat_id, "⚠️ Мало данных для прогноза. Введи минимум 20 чисел.")
                return "ok"

            counter = Counter(data)
            top = counter.most_common(5)

            msg = "🔮 Прогноз по наиболее частым числам:\n"
            for num, count in top:
                msg += f"{num} — выпало {count} раз\n"

            bot.send_message(chat_id, msg)
            return "ok"

        try:
            num = int(text)
            if 1 <= num <= 37:
                data = load_data()
                data.append(num)
                save_data(data)
                bot.send_message(chat_id, f"✅ Число {num} сохранено.")
            else:
                bot.send_message(chat_id, "❌ Вводи только числа от 1 до 37.")
        except:
            bot.send_message(chat_id, "❌ Не понимаю команду. Отправь число или /predict")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
