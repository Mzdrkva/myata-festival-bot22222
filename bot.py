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

# ====== Русские названия месяцев ======
MONTH_NAMES = {
    1: "января",   2: "февраля",  3: "марта",
    4: "апреля",   5: "мая",      6: "июня",
    7: "июля",     8: "августа",  9: "сентября",
    10: "октября", 11: "ноября",  12: "декабря",
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
        ("2025-06-14 00:30", "The OM"),       # попадёт к 13 июня
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
        ("2025-06-15 00:30", "ЗАЛЕЗ"),       # попадёт к 14 июня
        ("2025-06-15 12:20", "Хохма"),
        ("2025-06-15 13:20", "Cardio killer"),
        ("2025-06-15 14:20", "Можем хуже"),
        ("2025-06-15 15:20", "Breaking system"),
        ("2025-06-15 16:20", "Stigmata"),
        ("2025-06-15 17:20", "Jane air"),
    ],
    "Сцена 3": [],
    "Сцена 4": [],
    "Сцена 5": [],
    "Сцена 6": [],
    "Сцена 7": [],
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
main_kb.row("FAQ", "Расписание сцен", "⭐ Избранное")

schedule_kb = ReplyKeyboardMarkup(resize_keyboard=True)
schedule_kb.row("SIRENA", "TITANA", "Сцена 3", "Сцена 4")
schedule_kb.row("Сцена 5", "Сцена 6", "Сцена 7", "◀️ Главное меню")

date_kb = ReplyKeyboardMarkup(resize_keyboard=True)
date_kb.row("13 июня", "14 июня", "15 июня")
date_kb.row("◀️ Главное меню")

faq_options = [
    "О фестивале",
    "Обмен билетов на браслеты",
    "Место на парковке",
    "Место под палатку",
    "Карта Фестиваля",
    "Расписание работы душевых",
    "Расписание зон с кипятком",
    "Трансферы",
    "Расписание электричек"
]
faq_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for i in range(0, len(faq_options), 2):
    faq_kb.row(*(KeyboardButton(text) for text in faq_options[i:i+2]))
faq_kb.row(KeyboardButton("◀️ Главное меню"))

# ====== Фильтрация расписания по дате ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES[scene]:
        dt = datetime.fromisoformat(tstr)
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < time(2,0)):
            result.append((tstr, artist))
    return result

# ====== Хэндлеры ======
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply(
        "👋 Добро пожаловать в бот фестиваля «Мята 2025»!\n\nВыбери раздел:",
        reply_markup=main_kb
    )

@dp.message_handler(lambda m: m.text == "FAQ")
async def open_faq(message: types.Message):
    await message.reply("❓ FAQ — выбери тему:", reply_markup=faq_kb)

@dp.message_handler(lambda m: m.text == "Расписание сцен")
async def open_schedule(message: types.Message):
    await message.reply("📆 Выбери сцену:", reply_markup=schedule_kb)

@dp.message_handler(lambda m: m.text == "⭐ Избранное")
async def show_favorites(message: types.Message):
    user_id = str(message.from_user.id)
    picks = load_data().get(user_id, [])
    if not picks:
        return await message.reply("У тебя ещё нет избранного.", reply_markup=main_kb)

    lines = []
    for e in sorted(picks, key=lambda x: x["time"]):
        dt = datetime.fromisoformat(e["time"])
        date_str = f"{dt.day} {MONTH_NAMES[dt.month]}"
        time_str = dt.strftime("%H:%M")
        lines.append(f"{date_str} в {time_str} | {e['scene']} | {e['artist']}")

    await message.reply("📋 Твоё избранное:\n" + "\n".join(lines),
                        reply_markup=main_kb)

@dp.message_handler(lambda m: m.text in SCENES)
async def choose_scene(message: types.Message):
    user_context[message.from_user.id] = message.text
    await message.reply(f"⏳ Сцена «{message.text}» выбрана. Выбери дату:",
                        reply_markup=date_kb)

@dp.message_handler(lambda m: m.text in ["13 июня","14 июня","15 июня"])
async def choose_date(message: types.Message):
    scene = user_context.get(message.from_user.id)
    if not scene:
        return await message.reply("Сначала выбери сцену.", reply_markup=schedule_kb)

    day = int(message.text.split()[0])
    iso_date = f"2025-06-{day:02d}"
    entries = get_entries_for_date(scene, iso_date)
    if not entries:
        return await message.reply("На эту дату расписание пусто.", reply_markup=schedule_kb)

    kb = InlineKeyboardMarkup(row_width=1)
    for idx, (tstr, artist) in enumerate(entries):
        kb.add(InlineKeyboardButton(
            f"{tstr[11:16]} — {artist}",
            callback_data=f"star|{scene}|{iso_date}|{idx}"
        ))

    await message.reply(f"🗓 Расписание «{scene}» на {message.text}:", reply_markup=kb)

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

@dp.message_handler(lambda m: m.text == "◀️ Главное меню")
async def back_to_main(message: types.Message):
    user_context.pop(message.from_user.id, None)
    await message.reply("Возвращаемся в главное меню:", reply_markup=main_kb)

@dp.message_handler(lambda m: m.text in faq_options)
async def handle_faq(message: types.Message):
    answers = {
        "О фестивале": "«Мята 2025» — это трёхдневный фестиваль...",
        "Обмен билетов на браслеты": "Обмен у входа с 10:00 до 22:00.",
        "Место на парковке": "Парковка возле главного въезда.",
        "Место под палатку": "Зона кемпинга рядом с озером.",
        "Карта Фестиваля": "Скачать карту: https://example.com/map.png",
        "Расписание работы душевых": "Душевые открыты 8:00–22:00.",
        "Расписание зон с кипятком": "Кипяток выдают в палатках №5 и №9.",
        "Трансферы": "Трансферы от ж/д станции каждые 30 мин.",
        "Расписание электричек": "Электрички отправляются в 07:45 и 18:20."
    }
    await message.reply(answers.get(message.text, "Информация скоро появится."), reply_markup=faq_kb)

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
                            text=(f"🔔 Через 15 минут: {entry['artist']} "
                                  f"({entry['scene']}) в {entry['time'][11:16]}")
                        )
                        entry["notified"] = True
                        updated = True
        if updated:
            save_data(data)
        await asyncio.sleep(60)

async def on_startup(dp: Dispatcher):
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    # сбросим webhook и очистим pending updates перед polling
    asyncio.run(bot.delete_webhook(drop_pending_updates=True))
    executor.start_polling(dp, skip_updates=True, reset_webhook=True, on_startup=on_startup)
