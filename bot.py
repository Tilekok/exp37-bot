# pip install aiogram numpy pandas

import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import numpy as np
from collections import defaultdict, Counter

# =====================
# 1️⃣ Получение токена из переменной окружения
# =====================
API_TOKEN = os.environ.get("8791083151:AAG7m-9zxN7AZuNFQXz0gjf5KGIOIijh9v4")
if not API_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN не установлена!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

HISTORY_FILE = "history.txt"

# =====================
# 2️⃣ Загрузка истории
# =====================
history = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            nums = list(map(int, line.strip().split()))
            if nums:
                history.append(nums)

# =====================
# 3️⃣ Анализ чисел
# =====================
def analyze(history):
    if not history:
        return {}

    flat = [n for game in history for n in game]

    freq = Counter(flat)
    last_seen = {i: -1 for i in range(1, 38)}
    for i, game in enumerate(history):
        for n in game:
            last_seen[n] = i
    recency = {n: len(history) - last_seen[n] for n in range(1, 38)}

    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(history)-1):
        for n1 in history[i]:
            for n2 in history[i+1]:
                transitions[n1][n2] += 1
    last_game = history[-1] if history else []
    transition_score = defaultdict(int)
    for n in last_game:
        for k, v in transitions[n].items():
            transition_score[k] += v

    scores = {}
    for n in range(1, 38):
        scores[n] = freq[n]*0.35 + recency[n]*0.25 + transition_score[n]*0.25

    total = sum(scores.values())
    probs = {n: (scores[n]/total)*100 for n in scores} if total > 0 else {}
    return probs

# =====================
# 4️⃣ Генерация стратегий
# =====================
def generate_strategies(history, top_n=7, variants=5):
    probs = analyze(history)
    if not probs:
        return [list(range(1, top_n+1))]*variants, {}

    strategies = []
    keys = list(probs.keys())
    values = np.array(list(probs.values()))
    values = values / values.sum()

    for _ in range(variants):
        choice = np.random.choice(keys, size=top_n, replace=False, p=values).tolist()
        strategies.append(choice)

    top = dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_n])
    return strategies, top

# =====================
# 5️⃣ Команды бота
# =====================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🤖 Бот Экспресс 37\n\n"
        "/add 5 12 23 7 — добавить историю\n"
        "/suggest — прогноз топ чисел\n"
        "/strategies — варианты комбинаций\n"
        "/stats — статистика топ чисел"
    )

@dp.message(Command("add"))
async def add(message: types.Message):
    try:
        nums = list(map(int, message.text.split()[1:]))
        if not nums:
            return await message.answer("Введите числа через пробел")
        if not all(1 <= n <= 37 for n in nums):
            return await message.answer("Числа только 1–37")

        history.append(nums)
        with open(HISTORY_FILE, "a") as f:
            f.write(" ".join(map(str, nums)) + "\n")
        await message.answer(f"Добавлено: {nums}")
    except:
        await message.answer("Пример: /add 5 12 23 7")

@dp.message(Command("suggest"))
async def suggest(message: types.Message):
    probs = analyze(history)
    if not probs:
        return await message.answer("Нет данных для прогноза")

    top = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:7]
    text = "🎯 Прогноз топ чисел с вероятностью:\n\n"
    for n, p in top:
        text += f"{n} → {p:.2f}%\n"
    await message.answer(text)

@dp.message(Command("strategies"))
async def strategies(message: types.Message):
    variants, top_probs = generate_strategies(history)
    if not variants:
        return await message.answer("Нет данных для стратегий")

    text = "🎲 Варианты комбинаций:\n\n"
    for i, var in enumerate(variants, 1):
        text += f"{i}: {var}\n"
    await message.answer(text)

@dp.message(Command("stats"))
async def stats(message: types.Message):
    if not history:
        return await message.answer("Нет данных")
    probs = analyze(history)
    top = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "📊 Топ 10 чисел по прогнозу:\n\n"
    for n, p in top:
        text += f"{n}: {p:.2f}%\n"
    await message.answer(text)

# =====================
# 6️⃣ Запуск бота
# =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
