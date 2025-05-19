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
WELCOME_IMAGE = "welcome.jpg"  # Положите файл welcome.jpg в корень проекта

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

# ====== Загрузка/сохранение данных ======
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
    # отправляем фото вместе с текстом
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
        festival_text = (
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
            "Kамilla Robertovna, CARDIO KILLER, Sula fray, obraza net, 3333, Собачий Lie, ХОХМА, "
            "The Translators, Манго Буст, Yan Dilan, Бюро, МОЛОДОСТЬ ВНУТРИ, Пальцева Экспириенс, "
            "Людмил Огурченко, Breaking System, Brodsky, uncle pecos, Стрио, соня хочет танцевать, "
            "Juzeppe Junior, Лолита Косс, Остыл, Melekess, El Mashe, Дедовский Свитер, Baby Cute, "
            "Антон Прокофьев, Breakpillzz, Мама не узнает, GOKK’N’TONY, Можем хуже, RASPUTНIKI (KZ), "
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
        await msg.reply(festival_text, reply_markup=faq_kb())
    else:
        await msg.reply("Информация скоро появится.", reply_markup=faq_kb())

# … остальные хэндлеры и напоминания остаются без изменений …

async def on_startup(dp: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(reminder_loop())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, reset_webhook=True, on_startup=on_startup)
