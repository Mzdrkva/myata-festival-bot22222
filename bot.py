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

# ====== Файлы данных ======
SCENES_FILE = "scenes.json"
FAVS_FILE   = "user_data.json"

# ====== Базовый словарь сцен ======
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
    ]
}

# ====== Инициализация бота ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== Утилиты для JSON ======
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

# ====== Загрузка/сохранение ======
SCENES = load_json(SCENES_FILE, DEFAULT_SCENES)
FAVS   = load_json(FAVS_FILE, {})

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
        kb.row(*(KeyboardButton(name) for name in names[i:i+2]))
    kb.row("◀️ Главное меню")
    return kb

def date_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("13 июня", "14 июня", "15 июня")
    kb.row("◀️ Главное меню")
    return kb

def faq_kb():
    opts = [
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
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(opts), 2):
        kb.row(*(KeyboardButton(o) for o in opts[i:i+2]))
    kb.row("◀️ Главное меню")
    return kb

# ====== Фильтрация по дате ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES.get(scene, []):
        dt = datetime.fromisoformat(tstr)
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < time(2,0)):
            result.append((tstr, artist))
    return result

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
    await msg.reply(welcome, reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "FAQ")
async def cmd_faq(msg: types.Message):
    await msg.reply("❓ FAQ — выберите тему:", reply_markup=faq_kb())

@dp.message_handler(lambda m: m.text in [
    "О фестивале",
    "Обмен билетов на браслеты",
    "Место на парковке",
    "Место под палатку",
    "Карта Фестиваля",
    "Расписание работы душевых",
    "Расписание зон с кипятком",
    "Трансферы",
    "Расписание электричек"
])
async def handle_faq(msg: types.Message):
    if msg.text == "О фестивале":
        text = (
            "Фестиваль «Дикая Мята» — крупнейший независимый музыкальный опен-эйр.\n"
            "Даты проведения: Заезд — с 18:00 12 июня, программа фестиваля — 13-15 июня.\n"
            "Место проведения: Тульская область, поселок Бунырево.\n\n"
            "В 2025 году зрителей на 7 сценах ждет более 120 концертов и dj-сетов. "
            "Рок, инди, фолк, альтернатива, фанк, джаз, электроника — мультиформатная «Дикая Мята» "
            "представляет артистов всех актуальных жанров.\n\n"
            "На фестивале выступят THE HATTERS, Три дня дождя, ZOLOTO, АРИЯ, ХЛЕБ, SALUKI, polnalyubvi, "
            "DRUMMATIX, Заточка, БАЗАР, Jane Air, TMNV, Пётр Налич, ГУДТАЙМС, Бонд с кнопкой, СмешBand, "
            "Luverance, Кирпичи Big Band, The OM, MONOLYT (IL), Stigmata, мытищи в огне, PALC, OLIGARKH, "
            "Мультfильмы, Драгни, Beautiful boys, хмыров, Manapart, Конец солнечных дней, "
            "Кamilla Robertovna, CARDIO KILLER, Sula fray, obraza net, 3333, Собачий Lie, ХОХМА, "
            "The Translators, Манго Буст, Yan Dilan, Бюро, МОЛОДОСТЬ ВНУТРИ, Пальцева Экспириенс, "
            "Людмил Огурченко, Breaking System, Brodsky, uncle pecos, Стрио, соня хочет танцевать, "
            "Juzeppe Junior, Лолита Косс, Остыл, Melekess, El Mashe, Дедовский Свитер, Baby Cute, "
            "Антон Прокофьев, Breakpillzz, Мама не узнает, GOKK’N’TONY, Можем хуже, RASPUTNIKI (KZ), "
            "Inna Syberia, без обид, Давай, LITHIUM, Каспий, Три вторых, Рубеж Веков, синдром главного героя, "
            "Koledova, я Софа, Mazzltoff, ielele, Polina Offline, Ник Брусковский, ROFMAN, летяга, "
            "Tabasco Band, Гнев Господень, Дисциплина безбольной биты, Hideout, Савелiчъ Бэнд, ParadigmA, "
            "Клуб 33 и другие, новые анонсы каждую неделю!\n\n"
            "«Дикая Мята» по праву считается самым комфортным опен-эйром страны. Организованная парковка, "
            "бесплатная питьевая вода и душевые с горячей водой, дорожки, выложенные тротуарной плиткой, "
            "освещенные палаточные кемпинги, которые размечены на улицы и индивидуальные места под палатки, "
            "комната матери и ребенка, бассейн, видовой ресторан и арт-амбар, sup-станция и лаундж-зоны.\n\n"
            "Фудкорт фестиваля предлагает кухни мира на любой вкус и кошелек, вегетарианскую зону и атмосферную "
            "перголу с блюдами от шеф-поваров.\n\n"
            "Также для гостей представлено множество развлечений:\n"
            "— В пространстве Green Age проходят йога-практики, экстатик дэнс, арт-медитации, "
            "мастер-классы по нейрографике и лекции о здоровом образе жизни.\n"
            "— В бьюти-зоне можно создать свой яркий фестивальный образ, здесь работают мастера брейдинга "
            "и макияжа, открыт барбершоп.\n"
            "— Гости с детьми особо ценят Территорию детства, где есть Детская сцена «Ариэль», работают "
            "карусели и аттракционы, проводятся бесплатные мастер-классы, открыт детский сад с опытными "
            "аниматорами, впервые примет участие студия анимационного кино «Мельница» — приедут любимые "
            "мультгерои Лунтик, Барбоскины и Три богатыря.\n"
            "— Большая фестивальная ярмарка собирает лучших мастеров хэндмейда, авторской одежды, аксессуаров "
            "и украшений со всей страны.\n"
            "— На спортивной площадке есть воркаут-зона, проходят турниры по пляжному волейболу.\n"
            "— Партнеры фестиваля предлагают бесконечное множество призовых активностей и лаундж-зоны "
            "для отдыха гостей.\n\n"
            "Фестиваль «Дикая Мята» — лето, музыка и любовь! Это будет легендарно!"
        )
        await msg.reply(text, reply_markup=faq_kb())
    else:
        await msg.reply("Информация скоро появится.", reply_markup=faq_kb())

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
        tm   = dt.strftime("%H:%M")
        lines.append(f"{date} в {tm} | {e['scene']} | {e['artist']}")
    await msg.reply("📋 Ваше избранное:\n" + "\n".join(lines
)), reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text in SCENES)
async def cmd_choose_scene(msg: types.Message):
    user_context[msg.from_user.id] = msg.text
    await msg.reply(f"Сцена «{msg.text}» выбрана. Выберите дату:",
                    reply_markup=date_menu_kb())

@dp.message_handler(lambda m: m.text in ["13 июня","14 июня","15 июня"])
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
    for idx, (tstr, artist) in enumerate(entries):
        kb.add(InlineKeyboardButton(f"{tstr[11:16]} — {artist}",
                   callback_data=f"fav|{scene}|{iso}|{idx}"))
    await msg.reply(f"Расписание «{scene}» на {msg.text}:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("fav|"))
async def cb_fav(cq: types.CallbackQuery):
    _, scene, iso, idx = cq.data.split("|", 3)
    idx = int(idx)
    tstr, artist = get_entries_for_date(scene, iso)[idx]
    uid = str(cq.from_user.id)
    FAVS.setdefault(uid, [])
    entry = {"scene": scene, "time": tstr, "artist": artist, "notified": False}
    if not any(x["scene"]==scene and x["time"]==tstr for x in FAVS[uid]):
        FAVS[uid].append(entry)
        save_json(FAVS_FILE, FAVS)
        await bot.answer_callback_query(cq.id, f"⭐ Добавлено «{artist}»")
    else:
        await bot.answer_callback_query(cq.id, "✅ Уже в избранном")

@dp.message_handler(lambda m: m.text == "◀️ Главное меню")
async def cmd_back(msg: types.Message):
    await msg.reply("Главное меню:", reply_markup=main_menu_kb())

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

async def reminder_loop():
    while True:
        now = datetime.now()
        changed = False
        for uid, picks in FAVS.items():
            for e in picks:
                if not e["notified"]:
                    et = datetime.fromisoformat(e["time"])
                    delta = (et - now).total_seconds()
                    if 0 < delta <= 15*60:
                        await bot.send_message(int(uid),
                            f"🔔 Через 15 минут: {e['artist']} ({e['scene']}) в {e['time'][11:16]}"
                        )
                        e["notified"] = True
                        changed = True
        if changed:
            save_json(FAVS_FILE, FAVS)
        await asyncio.sleep(60)

async def on_startup(dp: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        reset_webhook=True,
        on_startup=on_startup
    )
