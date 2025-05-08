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
        ("2025-06-13 16:00", "Luverance"),
        ("2025-06-13 17:00", "ГУДТАЙМС"),
        ("2025-06-13 18:00", "Polnalyubvi"),
        ("2025-06-13 19:00", "Заточка"),
        ("2025-06-13 20:00", "TMNV"),
        ("2025-06-13 21:00", "ХЛЕБ"),
        ("2025-06-13 22:40", "Три дня дождя"),
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
        ("2025-06-15 12:00", "СмешBand"),
        ("2025-06-15 13:00", "Мультfильмы"),
        ("2025-06-15 14:00", "obraza net"),
        ("2025-06-15 15:00", "Пётр Налич"),
        ("2025-06-15 16:00", "мытищи в огне"),
        ("2025-06-15 17:00", "Базар"),
        ("2025-06-15 18:00", "The Hatters"),
    ],
    "TITANA": [
        ("2025-06-13 16:00", "Baby Cute"),
        ("2025-06-13 16:40", "Пальцева Экспириенс"),
        ("2025-06-13 17:40", "Людмил Огурченко"),
        ("2025-06-13 18:40", "Бюро"),
        ("2025-06-13 19:40", "OLIGARKH"),
        ("2025-06-13 20:40", "Yan Dilan"),
        ("2025-06-13 21:50", "Конец солнечных дней"),
        ("2025-06-14 00:30", "The OM"),   # попадёт под 13 июня
        ("2025-06-14 12:00", "Три Вторых"),
        ("2025-06-14 12:50", "El Mashe"),
        ("2025-06-14 13:40", "Inna Syberia"),
        ("2025-06-14 14:40", "Остыл"),
        ("2025-06-14 15:40", "Manapart"),
        ("2025-06-14 16:40", "Juzeppe Junior"),
        ("2025-06-14 17:40", "Манго буст"),
        ("2025-06-14 18:40", "Хмыров"),
        ("2025-06-14 19:40", "Стрио"),
        ("2025-06-14 20:40", "Молодость внутри"),
        ("2025-06-14 21:50", "Лолита косс"),
        ("2025-06-15 00:30", "ЗАЛЕЗ"),    # попадёт под 14 июня
        ("2025-06-15 12:20", "Хохма"),
        ("2025-06-15 13:20", "Cardio killer"),
        ("2025-06-15 14:20", "Можем хуже"),
        ("2025-06-15 15:20", "Breaking system"),
        ("2025-06-15 16:20", "Stigmata"),
        ("2025-06-15 17:20", "Jane air"),
    ],
    "Сцена 3": [], "Сцена 4": [],
    "Сцена 5": [], "Сцена 6": [], "Сцена 7": [],
}

# ====== Контекст пользователя ======
user_context = {}

# ====== Загрузка/сохранение данных ======
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

date_kb = ReplyKeyboardMarkup(resize_keyboard=True)
date_kb.row(
    KeyboardButton("13 июня"),
    KeyboardButton("14 июня"),
    KeyboardButton("15 июня"),
)
date_kb.row(KeyboardButton("◀️ Назад"))

# ====== Функция для фильтрации по дате (с учётом перехода полуночи) ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES[scene]:
        dt = datetime.fromisoformat(tstr)
        if dt.date() == date_dt.date() or (
           dt.date() == next_dt.date() and dt.time() < time(2, 0)
        ):
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
    user_id = message.from_user.id
    scene = user_context.get(user_id)
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

    picks_sorted = sorted(picks, key=lambda e: e["time"])
    lines = []
    for e in picks_sorted:
        dt = datetime.fromisoformat(e["time"])
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        lines.append(f"{date_str} {time_str} | {e['scene']} | {e['artist']}")

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

    if not any(e["scene"] == scene and e["time"] == time_str and e["artist"] == artist for e in picks):
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
                    if 0 < delta <= 15 * 60:
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
    # удаляем возможный webhook, чтобы не было конфликта polling
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
