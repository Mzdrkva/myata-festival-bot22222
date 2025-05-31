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

# ====== Загрузка конфигурации ======
# Создайте рядом с bot.py файл config.json с таким содержанием:
# {
#   "BOT_TOKEN": "<ВАШ_ТОКЕН_ОТ_BOTFATHER>",
#   "ADMIN_IDS": [<ID1>, <ID2>]
# }
CONFIG = load_json("config.json", {})
BOT_TOKEN = CONFIG.get("BOT_TOKEN", "")
ADMIN_IDS = CONFIG.get("ADMIN_IDS", [])

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ====== Русские названия месяцев ======
MONTH_NAMES = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}
# Обратная маппа: "мая" → 5
MONTH_RUS_TO_NUM = {v: k for k, v in MONTH_NAMES.items()}

# ====== Файлы данных ======
SCENES_FILE   = "scenes.json"
FAVS_FILE     = "user_data.json"
WELCOME_IMAGE = "welcome.jpg"

# ====== Стартовое расписание сцен для тестирования ======
DEFAULT_SCENES = {
    "Test": [
        ["2025-05-31 12:15", "Тестовый Артист"]
    ]
}
SCENES = load_json(SCENES_FILE, DEFAULT_SCENES)
FAVS   = load_json(FAVS_FILE, {})

# ====== Контекст выбора сцены ======
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
    # Вычисляем "сегодня" в формате "D месяц"
    now = datetime.now()
    day = now.day
    month_rus = MONTH_NAMES[now.month]
    today_str = f"{day} {month_rus}"
    kb.row(today_str)
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
        "В 2025 году зрителей на 7 сценах ждет более 120 концертов и dj-сетов. "
        "Рок, инди, фолк, альтернатива, фанк, джаз, электроника — мультиформатная «Дикая Мята» "
        "представляет артистов всех актуальных жанров.\n\n"
        "На фестивале выступят THE HATTERS, Три дня дождя, ZOLOTO, АРИЯ, ХЛЕБ, SALUKI, polnalyubvi, "
        "DRUMMATIX, Заточка, БАЗАР, Jane Air, TMNV, Пётр Налич, ГУДТАЙМС, Бонд с кнопкой, СмешBand, "
        "Luverance, Кирпичи Big Band, The OM, MONOLYT (IL), Stigmata, мытищи в огне, PALC, OLIGARKH, "
        "Мультfильмы, Драгни, Beautiful boys, хмыров, Manapart, Конец солнечных дней, Кamilla Robertovna, "
        "CARDIO KILLER, Sula fray, obraza net, 3333, Собачий Lie, ХОХМА, The Translators, Манго Буст, "
        "Yan Dilan, Бюро, МОЛОДОСТЬ ВНУТРИ, Пальцева Экспириенс, Людмил Огурченко, Breaking System, "
        "Brodsky, uncle pecos, Стрио, соня хочет танцевать, Juzeppe Junior, Лолита Косс, Остыл, Melekess, "
        "El Mashe, Дедовский Свитер, Baby Cute, Антон Прокофьев, Breakpillzz, Мама не узнает, GOKK’N’TONY, "
        "Можем хуже, RASPUTНIKI (KZ), Inna Syberia, без обид, Давай, LITHIUM, Каспий, Три вторых, Рубеж Веков, "
        "синдром главного героя, Koledova, я Софа, Mazzltoff, ielele, Polina Offline, Ник Брусковский, ROFMAN, "
        "летяга, Tabasco Band, Гнев Господень, Дисциплина безбольной биты, Hideout, Савелiчъ Бэнд, ParadigmA, "
        "Клуб 33 и другие, новые анонсы каждую неделю!\n\n"
        "«Дикая Мята» по праву считается самым комфортным опен-эйром страны. Организованная парковка, "
        "бесплатная питьевая вода и душевые с горячей водой, дорожки, выложенные тротуарной плиткой, "
        "освещенные палаточные кемпинги, которые размечены на улицы и индивидуальные места под палатки, "
        "комната матери и ребенка, бассейн, видовой ресторан и арт-амбар, sup-станция и лаундж-зоны.\n"
        "Фудкорт фестиваля предлагает кухни мира на любой вкус и кошелек, вегетарианскую зону и атмосферную "
        "перголу с блюдами от шеф-поваров.\n\n"
        "Также для гостей представлено множество развлечений:\n"
        "— В пространстве Green Age проходят йога-практики, экстатик дэнс, арт-медитации, "
        "мастер-классы по нейрографике и лекции о здоровом образе жизни.\n"
        "— В бьюти-зоне можно создать свой яркий фестивальный образ, здесь работают мастера брейдинга "
        "и макияжа, открыт барбершоп.\n"
        "— Гости с детьми особо ценят Территорию детства, где есть Детская сцена «Ариэль», работают "
        "карусели и аттракционы, проводятся бесплатные мастер-классы, открыт детский сад с опытными "
        "аниматорами, в этом году впервые примет участие студия анимационного кино «Мельница» — приедут "
        "любимые мультгерои Лунтик, Барбоскины и Три богатыря.\n"
        "— Большая фестивальная ярмарка собирает лучших мастеров хэндмейда, авторской одежды, аксессуаров "
        "и украшений со всей страны.\n"
        "— На спортивной площадке есть воркаут-зона, проходят турниры по пляжному волейболу.\n"
        "— Партнеры фестиваля предлагают бесконечное множество призовых активностей и лаундж-зоны "
        "для отдыха гостей.\n\n"
        "Фестиваль «Дикая Мята» — лето, музыка и любовь! Это будет легендарно!"
    ),
    "Обмен билетов на браслеты": "Текст по теме «Обмен билетов на браслеты»...",
    "Место на парковке": "Текст по теме «Место на парковке»...",
    "Место под палатку": "Текст по теме «Место под палатку»...",
    "Карта Фестиваля": "Текст по теме «Карта Фестиваля»...",
    "Расписание работы душевых": "Текст по теме «Расписание работы душевых»...",
    "Расписание зон с кипятком": "Текст по теме «Расписание зон с кипятком»...",
    "Трансферы": "Текст по теме «Трансферы»...",
    "Расписание электричек": "Текст по теме «Расписание электричек»..."
}

# ====== Вспомогательная функция для получения выступлений по дате ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES.get(scene, []):
        dt = datetime.fromisoformat(tstr)
        # Если время < 02:00 следующего дня, относим выступление к предыдущему дню
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < dtime(2, 0)):
            result.append((tstr, artist))
    return result

# ====== Фоновая задача: проверка избранного и уведомлений ======
async def reminder_loop():
    while True:
        now = datetime.utcnow()  # работаем в UTC
        updated = False
        for uid, picks in FAVS.items():
            for e in picks:
                if not e.get("notified", False):
                    perf_dt = datetime.fromisoformat(e["time"])
                    # Если время выступления < 02:00, относим к предыдущему дню
                    if perf_dt.time() < dtime(2, 0):
                        perf_dt -= timedelta(days=1)
                    delta = (perf_dt - now).total_seconds()
                    if 0 < delta <= 15 * 60:
                        # Отправляем напоминание
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
    uid = str(msg.from_user.id)
    FAVS.setdefault(uid, [])
    save_json(FAVS_FILE, FAVS)

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

@dp.message_handler(commands=['servertime'])
async def cmd_servertime(msg: types.Message):
    now = datetime.utcnow()
    await msg.reply(f"Серверное время (UTC): {now.strftime('%Y-%m-%d %H:%M')}")

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
        # Показываем дату в формате "D месяц"
        date = f"{dt.day} {MONTH_NAMES[dt.month]}"
        tm   = dt.strftime("%H:%M")
        lines.append(f"{date} в {tm} | {e['scene']} | {e['artist']}")
    await msg.reply("📋 Ваше избранное:\n" + "\n".join(lines), reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text in SCENES)
async def cmd_choose_scene(msg: types.Message):
    user_context[msg.from_user.id] = msg.text
    await msg.reply(f"Сцена «{msg.text}» выбрана. Выберите дату:", reply_markup=date_menu_kb())

@dp.message_handler(lambda m: True if len(m.text.split()) == 2 and m.text.split()[1] in MONTH_RUS_TO_NUM else False)
async def cmd_choose_date(msg: types.Message):
    scene = user_context.get(msg.from_user.id)
    if not scene:
        return await msg.reply("Сначала выберите сцену.", reply_markup=schedule_menu_kb())

    parts = msg.text.split()
    day = int(parts[0])
    month_rus = parts[1]
    month_num = MONTH_RUS_TO_NUM.get(month_rus)
    if not month_num:
        return await msg.reply("Непонятный месяц.", reply_markup=schedule_menu_kb())

    year = 2025
    iso = f"{year}-{month_num:02d}-{day:02d}"
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
    if msg.from_user.id not in ADMIN_IDS:
        return
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
    if msg.from_user.id not in ADMIN_IDS:
        return
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
    if msg.from_user.id not in ADMIN_IDS:
        return
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
    if msg.from_user.id not in ADMIN_IDS:
        return
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

@dp.message_handler(commands=['broadcast'])
async def cmd_broadcast(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply("Использование: /broadcast Текст сообщения")
    text = parts[1].strip()
    count = 0
    for uid in FAVS.keys():
        try:
            await bot.send_message(int(uid), f"📢 Сообщение от организаторов:\n{text}")
            count += 1
        except:
            pass
    await msg.reply(f"✅ Отправлено сообщений {count} пользователям.")

# ====== Запуск и обработка конфликтов ======
async def on_startup(dp: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
            break
        except TerminatedByOtherGetUpdates:
            asyncio.get_event_loop().run_until_complete(
                bot.delete_webhook(drop_pending_updates=True)
            )
            time.sleep(1)
