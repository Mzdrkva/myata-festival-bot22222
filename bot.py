import os
import json
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# ====== Настройки ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "user_data.json"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== Расписания сцен (сплошной список) ======
SCENES = {
    "SIRENA": [
        ("2025-06-13 15:00", "SULA FRAY"),
        ("2025-06-13 16:00", "Luverance"),
        # ... полный список SIRENA ...
    ],
    "TITANA": [
        ("2025-06-13 16:00", "Baby Cute"),
        ("2025-06-13 16:40", "Пальцева Экспириенс"),
        # ... полный список TITANA ...
    ],
    "Сцена 3": [], "Сцена 4": [], "Сцена 5": [], "Сцена 6": [], "Сцена 7": []
}

# Состояние пользователя: какая сцена выбрана
user_context = {}

# ====== Утилиты ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Главное меню ======
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(
    KeyboardButton("SIRENA"),
    KeyboardButton("TITANA"),
    KeyboardButton("Сцена 3"),
    KeyboardButton("Сцена 4"),
)
main_kb.row(
    KeyboardButton("Сцена 5"),
    KeyboardButton("Сцена 6"),
    KeyboardButton("Сцена 7"),
    KeyboardButton("⭐ Избранное"),
)

# Клавиатура дат
date_kb = ReplyKeyboardMarkup(resize_keyboard=True)
date_kb.row(
    KeyboardButton("13 июня"),
    KeyboardButton("14 июня"),
    KeyboardButton("15 июня"),
)
date_kb.row(KeyboardButton("◀️ Назад"))

# ====== Хэндлеры ======

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    text = (
        "🌿 Мята 2025 — это не просто фестиваль, а три дня музыки, природы и полной перезагрузки. 🎶🔥\n\n"
        "🤖 С этим ботом ты можешь:\n"
        "– выбирать любимые выступления\n"
        "– смотреть расписание по сценам и датам\n"
        "– получать напоминания за 15 минут до старта\n\n"
        "Выбери сцену или открой избранное:"
    )
    await message.reply(text, reply_markup=main_kb)

@dp.message_handler(lambda m: m.text in SCENES.keys())
async def choose_scene(message: types.Message):
    scene = message.text
    user_context[message.from_user.id] = scene
    await message.reply(
        f"⏳ Выбрана сцена {scene}. Выбери дату:",
        reply_markup=date_kb
    )

@dp.message_handler(lambda m: m.text in ["13 июня", "14 июня", "15 июня"])
async def choose_date(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_context:
        return await message.reply("Сначала выбери сцену.", reply_markup=main_kb)
    scene = user_context[user_id]
    # Преобразуем текст даты в ISO
    day = message.text.split()[0]
    iso_date = f"2025-06-{int(day):02d}"
    # Фильтруем расписание сцены по дате
    entries = [
        (t,a) for t,a in SCENES[scene]
        if t.startswith(iso_date)
    ]
    if not entries:
        return await message.reply("На эту дату расписание пусто.", reply_markup=main_kb)
    kb = InlineKeyboardMarkup(row_width=2)
    for idx, (tstr, artist) in enumerate(entries):
        time_only = tstr[11:16]
        kb.insert(InlineKeyboardButton(time_only, callback_data=f"star|{scene}|{iso_date}|{idx}"))
    await message.reply(f"🗓 Расписание {scene} на {message.text}:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "◀️ Назад")
async def back_to_main(message: types.Message):
    user_context.pop(message.from_user.id, None)
    await message.reply("Вернулся в главное меню:", reply_markup=main_kb)

@dp.message_handler(lambda m: m.text == "⭐ Избранное")
async def show_favorites(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data().get(user_id, [])
    if not data:
        return await message.reply("У тебя ещё нет избранного.", reply_markup=main_kb)
    lines = sorted(data, key=lambda e: e["time"])
    text = "📋 Твоё избранное:\n" + "\n".join(
        f"{e['time']} — {e['scene']}: {e['artist']}" for e in lines
    )
    await message.reply(text, reply_markup=main_kb)

@dp.callback_query_handler(lambda c: c.data.startswith("star|"))
async def handle_star(callback: types.CallbackQuery):
    _, scene, iso_date, idx_str = callback.data.split("|", 3)
    idx = int(idx_str)
    entries = [(t,a) for t,a in SCENES[scene] if t.startswith(iso_date)]
    time_str, artist = entries[idx]
    user_id = str(callback.from_user.id)
    data = load_data()
    picks = data.get(user_id, [])
    entry = {"scene": scene, "time": time_str, "artist": artist, "notified": False}
    if not any(e["scene"]==scene and e["time"]==time_str for e in picks):
        picks.append(entry)
        data[user_id] = picks
        save_data(data)
        await bot.answer_callback_query(callback.id, f"⭐ Добавлено: {artist}")
    else:
        await bot.answer_callback_query(callback.id, "✅ Уже в избранном")

# ====== Фоновый таск для напоминаний ======
async def reminder_loop():
    while True:
        now = datetime.now()
        data = load_data()
        updated = False
        for uid, picks in data.items():
            for entry in picks:
                if not entry["notified"]:
                    event_time = datetime.fromisoformat(entry["time"])
                    delta = (event_time - now).total_seconds()
                    if 0 < delta <= 15*60:
                        await bot.send_message(
                            chat_id=int(uid),
                            text=(
                                f"🔔 Через 15 минут: {entry['artist']} "
                                f"({entry['scene']}) в {entry['time'][11:16]}"
                            )
                        )
                        entry["notified"] = True
                        updated = True
        if updated:
            save_data(data)
        await asyncio.sleep(60)

async def on_startup(dp: Dispatcher):
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
