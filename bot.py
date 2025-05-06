import os
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# ====== Настройки ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "user_data.json"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== Расписание SIRENA ======
# Формат: "YYYY-MM-DD HH:MM" — время начала
SIRENA_SCHEDULE = [
    # 13 июня (пятница)
    ("2025-06-13 15:00", "SULA FRAY"),
    ("2025-06-13 16:00", "Luverance"),
    ("2025-06-13 17:00", "ГУДТАЙМС"),
    ("2025-06-13 18:00", "Polnalyubvi"),
    ("2025-06-13 19:00", "Заточка"),
    ("2025-06-13 20:00", "TMNV"),
    ("2025-06-13 21:00", "ХЛЕБ"),
    ("2025-06-13 22:40", "Три дня дождя"),
    # 14 июня (суббота)
    ("2025-06-14 13:00", "The Translators"),
    ("2025-06-14 14:00", "PALC"),
    ("2025-06-14 15:00", "Beautiful boys"),
    ("2025-06-14 16:00", "3333"),
    ("2025-06-14 17:00", "Драгни"),
    ("2025-06-14 18:00", "Кирпичи Big Band"),
    ("2025-06-14 19:00", "DRUMMATIX"),
    ("2025-06-14 20:00", "Saluki"),
    ("2025-06-14 21:00", "ZOLOTO"),
    ("2025-06-14 22:40", "АРИЯ"),
    # 15 июня (воскресенье)
    ("2025-06-15 12:00", "СмешBand"),
    ("2025-06-15 13:00", "Мультfильмы"),
    ("2025-06-15 14:00", "obraza net"),
    ("2025-06-15 15:00", "Пётр Налич"),
    ("2025-06-15 16:00", "мытищи в огне"),
    ("2025-06-15 17:00", "Базар"),
    ("2025-06-15 18:00", "The Hatters"),
]

# ====== Утилиты: загрузка/сохранение ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Хэндлеры ======
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    text = (
        "🎵 Добро пожаловать на сцену SIRENA!\n\n"
        "Команды:\n"
        "/schedule — показать расписание\n"
        "/mypick — посмотреть свой план\n"
        "\nВыберите артистов в избранное через /schedule"
    )
    await message.reply(text)

@dp.message_handler(commands=['schedule'])
async def cmd_schedule(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    for time_str, artist in SIRENA_SCHEDULE:
        btn = InlineKeyboardButton(
            text=f"{time_str[11:16]} — {artist}",
            callback_data=f"star|{time_str}|{artist}"
        )
        kb.insert(btn)
    await message.reply("⏰ Расписание SIRENA:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("star|"))
async def handle_star(callback_query: types.CallbackQuery):
    _, time_str, artist = callback_query.data.split("|", 2)
    user_id = str(callback_query.from_user.id)
    data = load_data()
    picks = data.get(user_id, [])
    entry = {"time": time_str, "artist": artist}
    if entry not in picks:
        picks.append(entry)
        data[user_id] = picks
        save_data(data)
        await bot.answer_callback_query(callback_query.id, text=f"⭐ Добавлено в твой план: {artist}")
    else:
        await bot.answer_callback_query(callback_query.id, text=f"Уже в твоём плане: {artist}")

@dp.message_handler(commands=['mypick'])
async def cmd_mypick(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()
    picks = data.get(user_id, [])
    if not picks:
        await message.reply("Ты ещё не выбрал ни одного артиста. Напиши /schedule")
        return
    # Сортируем по времени
    picks_sorted = sorted(picks, key=lambda e: e["time"])
    lines = [f"{e['time'][11:16]} — {e['artist']}" for e in picks_sorted]
    await message.reply("📋 Твой план на SIRENA:\n" + "\n".join(lines))

# ====== Запуск ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
