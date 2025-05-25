import os
import json
import asyncio
import time
from datetime import datetime, timedelta, time as dtime

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates

# ====== Русские названия месяцев ======
MONTH_NAMES = {
    1: "января",   2: "февраля",  3: "марта",
    4: "апреля",   5: "мая",      6: "июня",
    7: "июля",     8: "августа",  9: "сентября",
    10: "октября", 11: "ноября",  12: "декабря",
}

# ====== Файлы данных и ресурсы ======
SCENES_FILE   = "scenes.json"
FAVS_FILE     = "user_data.json"
WELCOME_IMAGE = "welcome.jpg"

# ====== Стартовое расписание сцен ======
DEFAULT_SCENES = {
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
        ("2025-06-14 00:30", "The OM"),
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
        ("2025-06-15 00:30", "Бонд с кнопкой"),
        ("2025-06-15 12:20", "Хохма"),
        ("2025-06-15 13:20", "Cardio killer"),
        ("2025-06-15 14:20", "Можем хуже"),
        ("2025-06-15 15:20", "Breaking system"),
        ("2025-06-15 16:20", "Stigmata"),
        ("2025-06-15 17:20", "Jane air"),
    ],
    "Маяк": [
        ("2025-06-13 15:20", "HIDeout"),
        ("2025-06-13 16:20", "Rofman"),
        ("2025-06-13 17:20", "Koledova"),
        ("2025-06-13 18:20", "Без обид"),
        ("2025-06-13 19:20", "Антон прокофьев"),
        ("2025-06-13 20:20", "Синдром главного героя"),
        ("2025-06-13 21:50", "собачий lie"),
        ("2025-06-14 12:20", "tabasco band"),
        ("2025-06-14 13:20", "мама не узнает"),
        ("2025-06-14 14:20", "brodsky"),
        ("2025-06-14 15:20", "lithium"),
        ("2025-06-14 16:20", "Дедовский свитер"),
        ("2025-06-14 17:20", "Давай"),
        ("2025-06-14 18:20", "Uncle pecos"),
        ("2025-06-14 19:20", "Rasputniki"),
        ("2025-06-14 20:20", "Melekess"),
        ("2025-06-14 21:50", "Monolyt (IL)"),
        ("2025-06-15 11:40", "Mazzltoff"),
        ("2025-06-15 12:40", "Дисциплина безбольной биты"),
        ("2025-06-15 13:40", "Ник брусковский"),
        ("2025-06-15 14:40", "Рубеж веков"),
        ("2025-06-15 15:40", "Каспий"),
        ("2025-06-15 16:40", "kamilla robertovna"),
    ],
}

# ====== Инициализация бота ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== JSON утилиты ======
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default.copy()

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Загрузка/сохранение данных ======
SCENES = load_json(SCENES_FILE, DEFAULT_SCENES)
FAVS = load_json(FAVS_FILE, {})

# ====== Контекст пользователя ======
user_context = {}

# ====== Клавиатуры ======
def main_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("FAQ", "Расписание сцен", "⭐ Избранное")
    return kb

def schedule_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    names = list(SCENES.keys())
    for i in range(0, len(names), 2):
        kb.row(*(KeyboardButton(n) for n in names[i:i+2]))
    kb.row("◀️ Главное меню")
    return kb

def date_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("13 июня", "14 июня", "15 июня")
    kb.row("◀️ Главное меню")
    return kb

def faq_kb():
    opts = [
        "О фестивале", "Обмен билетов на браслеты",
        "Место на парковке", "Место под палатку",
        "Карта Фестиваля", "Расписание работы душевых",
        "Расписание зон с кипятком", "Трансферы",
        "Расписание электричек"
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(opts), 2):
        kb.row(*(KeyboardButton(o) for o in opts[i:i+2]))
    kb.row("◀️ Главное меню")
    return kb

# ====== Тексты FAQ ======
FAQ_TEXTS = {
    "О фестивале": (
        "Фестиваль «Дикая Мята» — крупнейший независимый музыкальный опен-эйр.\n"
        "Даты проведения: Заезд — с 18:00 12 июня, программа фестиваля — 13-15 июня.\n"
        "Место проведения: Тульская область, поселок Бунырево.\n\n"
        "В 2025 году зрителей на 7 сценах ждет более 120 концертов и dj-сетов. Рок, инди, фолк, "
        "альтернатива, фанк, джаз, электроника — мультиформатная «Дикая Мята» представляет артистов всех "
        "актуальных жанров.\n\n"
        "На фестивале выступят THE HATTERS, Три дня дождя, ZOLOTO, АРИЯ, ХЛЕБ, SALUKI, polnalyubvi, "
        "DRUMMATIX, Заточка, БАЗАР, Jane Air, TMNV, Пётр Налич, ГУДТАЙМС, Бонд с кнопкой, СмешBand, "
        "Luverance, Кирпичи Big Band, The OM, MONOLYT (IL), Stigmata, мытищи в огне, PALC, OLIGARKH, "
        "Мультfильмы, Драгни, Beautiful boys, хмыров, Manapart, Конец солнечных дней, kamilla robertovna, "
        "Cardio killer, Sula fray, obraza net, 3333, Собачий Lie, Хохма, The Translators, Манго буст, "
        "Yan Dilan, Бюро, Молодость внутри, Пальцева Экспириенс, Людмил Огурченко, Breaking system, "
        "Brodsky, Uncle pecos, Стрио, Juzeppe Junior, Лолита косс, Остыл, Melekess, El Mashe, "
        "Дедовский свитер, Baby Cute, Антон Прокофьев, Mazzltoff, Tabasco Band, Дисциплина безбольной биты и другие.\n\n"
        "«Дикая Мята» по праву считается самым комфортным опен-эйром страны: организованная парковка, "
        "бесплатная питьевая вода и душевые с горячей водой, дорожки из плитки, освещенные палаточные "
        "кемпинги с размеченными местами, комната матери и ребенка, бассейн, видовой ресторан и арт-амбар, "
        "sup-станция и лаундж-зоны.\n\n"
        "Фудкорт предлагает кухни мира на любой вкус и кошелек, вегетарианскую зону и перголу от шеф-поваров.\n\n"
        "Программа развлечений:\n"
        "— Green Age: йога, экстатик дэнс, арт-медитации, мастер-классы, лекции.\n"
        "— Бьюти-зона: брейдинга, макияж, барбершоп.\n"
        "— Территория детства: Детская сцена «Ариэль», карусели, аттракционы, мастер-классы, аниматоры, "
        "мультгерои от «Мельницы».\n"
        "— Ярмарка хэндмейда и авторской одежды.\n"
        "— Спортивная площадка: воркаут, пляжный волейбол.\n"
        "— Призы и лаундж-зоны от партнеров.\n\n"
        "Фестиваль «Дикая Мята» — лето, музыка и любовь! Это будет легендарно!"
    ),
    "Обмен билетов на браслеты": "Текст по теме «Обмен билетов на браслеты»...",
    "Место на парковке": "Текст по теме «Место на парковке»...",
    "Место под палатку": "Текст по теме «Место под палатку»...",
    "Карта Фестиваля": "Текст по теме «Карта Фестиваля»...",
    "Расписание работы душевых": "Текст по теме «Расписание работы душевых»...",
    "Расписание зон с кипятком": "Текст по теме «Расписание зон с кипятком»...",
    "Трансферы": "Текст по теме «Трансферы»...",
    "Расписание электричек": "Текст по теме «Расписание электричек»...",
}

# ====== Вспомогательная функция по расписанию ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES.get(scene, []):
        dt = datetime.fromisoformat(tstr)
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < dtime(2, 0)):
            result.append((tstr, artist))
    return result

# ====== Фоновая задача: напоминания за 15 минут ======
async def reminder_loop():
    while True:
        now = datetime.now()
        updated = False
        for uid, picks in FAVS.items():
            for e in picks:
                if not e.get("notified", False):
                    perf_dt = datetime.fromisoformat(e["time"])
                    if perf_dt.time() < dtime(2, 0):
                        perf_dt -= timedelta(days=1)
                    delta = (perf_dt - now).total_seconds()
                    if 0 < delta <= 15 * 60:
                        await bot.send_message(
                            int(uid),
                            f"🔔 Через 15 минут: {e['artist']} ({e['scene']}) в {perf_dt.strftime('%H:%M')}"
                        )
                        e["notified"] = True
                        updated = True
        if updated:
            save_json(FAVS_FILE, FAVS)
        await asyncio.sleep(60)

# ====== Хэндлеры ======
@dp.message_handler(commands=['start'])
async def cmd_start(msg: types.Message):
    welcome = (
        "🌿 Мята 2025 — три дня музыки, природы и перезагрузки. 🎶🔥\n\n"
        "🤖 С этим ботом ты можешь:\n"
        "– выбирать любимые выступления\n"
        "– смотреть расписание по сценам и датам\n"
        "– получать напоминания за 15 минут до старта\n"
        "– просматривать ответы на часто задаваемые вопросы"
    )
    with open(WELCOME_IMAGE, "rb") as photo:
        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=photo,
            caption=welcome,
            reply_markup=main_menu_kb()
        )

@dp.message_handler(lambda m: m.text == "FAQ")
async def cmd_faq(msg: types.Message):
    await msg.reply("❓ FAQ — выберите тему:", reply_markup=faq_kb())

@dp.message_handler(lambda m: m.text in FAQ_TEXTS)
async def faq_answer(msg: types.Message):
    await msg.reply(FAQ_TEXTS[msg.text], reply_markup=faq_kb())

@dp.message_handler(lambda m: m.text == "Расписание сцен")
async def cmd_schedule(msg: types.Message):
    await msg.reply("📆 Выберите сцену:", reply_markup=schedule_menu_kb())

@dp.message_handler(lambda m: m.text == "⭐ Избранное")
async def cmd_favs(msg: types.Message):
    uid = str(msg.from_user.id)
    picks = FAVS.get(uid, [])
    if not picks:
        return await msg.reply("У вас нет избранного.", reply_markup=main_menu_kb())
    lines = []
    for e in sorted(picks, key=lambda x: x["time"]):
        dt = datetime.fromisoformat(e["time"])
        date = f"{dt.day} {MONTH_NAMES[dt.month]}"
        tm = dt.strftime("%H:%M")
        lines.append(f"{date} в {tm} | {e['scene']} | {e['artist']}")
    await msg.reply("📋 Ваше избранное:\n" + "\n".join(lines),
                    reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text in SCENES)
async def cmd_choose_scene(msg: types.Message):
    user_context[msg.from_user.id] = msg.text
    await msg.reply(f"Сцена «{msg.text}» выбрана. Выберите дату:", reply_markup=date_menu_kb())

@dp.message_handler(lambda m: m.text in ["13 июня", "14 июня", "15 июня"])
async def cmd_choose_date(msg: types.Message):
    scene = user_context.get(msg.from_user.id)
    if not scene:
        return await msg.reply("Сначала выберите сцену.", reply_markup=schedule_menu_kb())
    day = int(msg.text.split()[0])
    iso = f"2025-06-{day:02d}"
    entries = get_entries_for_date(scene, iso)
    if not entries:
        return await msg.reply("На эту дату нет выступлений.", reply_markup=schedule_menu_kb())
    kb = InlineKeyboardMarkup(row_width=1)
    for tstr, artist in entries:
        kb.add(InlineKeyboardButton(f"{tstr[11:16]} — {artist}", callback_data=f"fav|{scene}|{tstr}"))
    await msg.reply(f"Расписание «{scene}» на {msg.text}:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("fav|"))
async def cb_fav(cq: types.CallbackQuery):
    _, scene, tstr = cq.data.split("|", 2)
    artist = next(a for dt, a in SCENES.get(scene, []) if dt == tstr)
    uid = str(cq.from_user.id)
    FAVS.setdefault(uid, [])
    if not any(x["scene"] == scene and x["time"] == tstr for x in FAVS[uid]):
        FAVS[uid].append({"scene": scene, "time": tstr, "artist": artist, "notified": False})
        save_json(FAVS_FILE, FAVS)
        await bot.answer_callback_query(cq.id, f"⭐ Добавлено «{artist}»")
    else:
        await bot.answer_callback_query(cq.id, "✅ Уже в избранном")

@dp.message_handler(lambda m: m.text == "◀️ Главное меню")
async def cmd_back(msg: types.Message):
    await msg.reply("Главное меню:", reply_markup=main_menu_kb())

# ====== Админ-команды ======
@dp.message_handler(commands=['add_scene'])
async def cmd_add_scene(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply("Используйте: /add_scene Название_сцены")
    name = parts[1].strip()
    if name in SCENES:
        return await msg.reply("Такая сцена уже существует.")
    SCENES[name] = []
    save_json(SCENES_FILE, SCENES)
    await msg.reply(f"✅ Сцена «{name}» добавлена.")

@dp.message_handler(commands=['remove_scene'])
async def cmd_remove_scene(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply("Используйте: /remove_scene Название_сцены")
    name = parts[1].strip()
    if name not in SCENES:
        return await msg.reply(f"Сцена «{name}» не найдена.")
    del SCENES[name]
    save_json(SCENES_FILE, SCENES)
    await msg.reply(f"✅ Сцена «{name}» удалена.")

@dp.message_handler(commands=['add_perf'])
async def cmd_add_perf(msg: types.Message):
    try:
        _, payload = msg.text.split(maxsplit=1)
        scene, dt_str, artist = [s.strip() for s in payload.split('|', 2)]
    except ValueError:
        return await msg.reply(
            "Использование:\n"
            "/add_perf Сцена|YYYY-MM-DD HH:MM|Имя артиста"
        )
    if scene not in SCENES:
        return await msg.reply(f"Сцена «{scene}» не найдена.")
    SCENES[scene].append((dt_str, artist))
    save_json(SCENES_FILE, SCENES)
    await msg.reply(f"✅ Добавлено в «{scene}»: {dt_str} — {artist}")

@dp.message_handler(commands=['remove_perf'])
async def cmd_remove_perf(msg: types.Message):
    try:
        _, payload = msg.text.split(maxsplit=1)
        scene, dt_str, artist = [s.strip() for s in payload.split('|', 2)]
    except ValueError:
        return await msg.reply(
            "Использование:\n"
            "/remove_perf Сцена|YYYY-MM-DD HH:MM|Имя артиста"
        )
    if scene not in SCENES:
        return await msg.reply(f"Сцена «{scene}» не найдена.")
    entry = (dt_str, artist)
    if entry not in SCENES[scene]:
        return await msg.reply("Такого выступления нет.")
    SCENES[scene].remove(entry)
    save_json(SCENES_FILE, SCENES)
    await msg.reply(f"✅ Удалено из «{scene}»: {dt_str} — {artist}")

# ====== Запуск ======
async def on_startup(dp: Dispatcher):
    # сброс вебхука и удаление старых апдейтов
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    # в цикле убираем конфликт TerminatedByOtherGetUpdates и повторяем polling
    while True:
        try:
            executor.start_polling(
                dp,
                skip_updates=True,
                on_startup=on_startup
            )
            break
        except TerminatedByOtherGetUpdates:
            asyncio.get_event_loop().run_until_complete(
                bot.delete_webhook(drop_pending_updates=True)
            )
            time.sleep(1)
