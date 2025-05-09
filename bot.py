import os
import json
import asyncio
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# ====== Русские названия месяцев для избранного ======
MONTH_NAMES = {
    1: "января", 2: "февраля", 3: "марта",
    4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября",
    10: "октября", 11: "ноября", 12: "декабря",
}

# ====== Настройки ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "user_data.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== Расписания сцен ======
SCENES = {
    "SIRENA": [
        ("2025-06-13 15:00", "SULA FRAY"),
        # … полный список …
        ("2025-06-15 18:00", "The Hatters"),
    ],
    "TITANA": [
        ("2025-06-13 16:00", "Baby Cute"),
        # … полный список …
        ("2025-06-15 17:20", "Jane air"),
    ],
    "Сцена 3": [], "Сцена 4": [],
    "Сцена 5": [], "Сцена 6": [], "Сцена 7": [],
}

# Контекст (какую сцену выбрал пользователь)
user_context = {}

# ====== Утилиты для работы с данными ======
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Клавиатуры ======
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row("SIRENA", "TITANA", "Сцена 3", "Сцена 4")
main_kb.row("Сцена 5", "Сцена 6", "Сцена 7", "⭐ Избранное")

date_kb = ReplyKeyboardMarkup(resize_keyboard=True)
date_kb.row("13 июня", "14 июня", "15 июня")
date_kb.row("◀️ Назад")

# ====== Фильтрация расписания по дате (учёт “ночи”) ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES[scene]:
        dt = datetime.fromisoformat(tstr)
        # либо тот же день, либо следующая ночь до 02:00
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < time(2, 0)):
            result.append((tstr, artist))
    return result

# ====== Хэндлеры ======
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    text = (
        "🌿 Мята 2025 — три дня музыки, природы и перезагрузки. 🎶🔥\n\n"
        "🤖 С этим ботом ты можешь:\n"
        "– выбирать любимые выступления\n"
        "– смотреть расписание по сценам и датам\n"
        "– получать напоминания за 15 минут до старта\n\n"
        "Выбери сцену или нажми ⭐ Избранное:"
    )
    await message.reply(text, reply_markup=main_kb)

@dp.message_handler(lambda m: m.text in SCENES)
async def choose_scene(message: types.Message):
    user_context[message.from_user.id] = message.text
    await message.reply(f"⏳ Сцена {message.text} выбрана. Выбери дату:", reply_markup=date_kb)

@dp.message_handler(lambda m: m.text in ["13 июня", "14 июня", "15 июня"])
async def choose_date(message: types.Message):
    scene = user_context.get(message.from_user.id)
    if not scene:
        return await message.reply("Сначала выбери сцену.", reply_markup=main_kb)

    day = int(message.text.split()[0])
    iso_date = f"2025-06-{day:02d}"
    entries = get_entries_for_date(scene, iso_date)
    if not entries:
        return await message.reply("На эту дату расписание пусто.", reply_markup=main_kb)

    kb = InlineKeyboardMarkup(row_width=2)
    for idx, (tstr, artist) in enumerate(entries):
        time_only = tstr[11:16]
        kb.insert(InlineKeyboardButton(
            f"{time_only} — {artist}",
            callback_data=f"star|{scene}|{iso_date}|{idx}"
        ))
    await message.reply(f"🗓 Расписание {scene} на {message.text}:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "◀️ Назад")
async def back_to_main(message: types.Message):
    user_context.pop(message.from_user.id, None)
    await message.reply("Вернулся в главное меню.", reply_markup=main_kb)

@dp.message_handler(lambda m: m.text == "⭐ Избранное")
async def show_favorites(message: types.Message):
    user_id = str(message.from_user.id)
    picks = load_data().get(user_id, [])
    if not picks:
        return await message.reply("У тебя ещё нет избранного.", reply_markup=main_kb)

    picks_sorted = sorted(picks, key=lambda x: x["time"])
    lines = []
    for e in picks_sorted:
        dt = datetime.fromisoformat(e["time"])
        date_str = f"{dt.day} {MONTH_NAMES[dt.month]}"
        time_str = dt.strftime("%H:%M")
        lines.append(f"{date_str} в {time_str} | {e['scene']} | {e['artist']}")

    await message.reply("📋 Твоё избранное:\n" + "\n".join(lines), reply_markup=main_kb)

@dp.callback_query_handler(lambda c: c.data.startswith("star|"))
async def handle_star(callback: types.CallbackQuery):
    _, scene, iso_date, idx_str = callback.data.split("|", 3)
    idx = int(idx_str)
    entries = get_entries_for_date(scene, iso_date)
    time_str, artist = entries[idx]

    user_id = str(callback.from_user.id)
    data = load_data()
    picks = data.get(user_id, [])
    entry = {"scene": scene, "time": time_str, "artist": artist, "notified": False}
    if not any(x["scene"] == scene and x["time"] == time_str for x in picks):
        picks.append(entry)
        data[user_id] = picks
        save_data(data)
        await bot.answer_callback_query(callback.id, f"⭐ Добавлено: {artist}")
    else:
        await bot.answer_callback_query(callback.id, "✅ Уже в избранном")

# ====== Фоновый таск напоминаний ======
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
                            text=(f"🔔 Через 15 минут: {entry['artist']} "
                                  f"({entry['scene']}) в {entry['time'][11:16]}")
                        )
                        entry["notified"] = True
                        updated = True
        if updated:
            save_data(data)
        await asyncio.sleep(60)

# ====== Запуск ======
if __name__ == "__main__":
    # Синхронно удаляем все webhooks и pending updates
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))

    # Старт polling с удалённым webhook
    executor.start_polling(
        dp,
        skip_updates=True,
        reset_webhook=True,
        on_startup=lambda _dp: asyncio.create_task(reminder_loop())
    )
