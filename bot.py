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
# Убедитесь, что рядом с bot.py есть config.json:
# {
#   "BOT_TOKEN": "<ВАШ_ТОКЕН>",
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
    1: "января",   2: "февраля",  3: "марта",
    4: "апреля",   5: "мая",      6: "июня",
    7: "июля",     8: "августа",  9: "сентября",
    10: "октября", 11: "ноября",  12: "декабря",
}

# ====== Файлы данных и ресурсы ======
SCENES_FILE   = "scenes.json"
FAVS_FILE     = "user_data.json"
WELCOME_IMAGE = "welcome.jpg"  # Поместите рядом с bot.py

# ====== Стартовое расписание сцен (если отсутствует scenes.json) ======
DEFAULT_SCENES = {
    "SIRENA": [
        ["2025-06-13 15:00", "SULA FRAY"],
        ["2025-06-13 16:00", "Luverance"],
        ["2025-06-13 17:00", "ГУДТАЙМС"],
        ["2025-06-13 18:00", "Polnalyubvi"],
        ["2025-06-13 19:00", "Заточка"],
        ["2025-06-13 20:00", "TMNV"],
        ["2025-06-13 21:00", "ХЛЕБ"],
        ["2025-06-13 22:40", "Три дня дождя"],
        ["2025-06-14 13:00", "The Translators"],
        ["2025-06-14 14:00", "PALC"],
        ["2025-06-14 15:00", "Beautiful boys"],
        ["2025-06-14 16:00", "3333"],
        ["2025-06-14 17:00", "Драгни"],
        ["2025-06-14 18:00", "Кирпичи Big Band"],
        ["2025-06-14 19:00", "DRUMMATIX"],
        ["2025-06-14 20:00", "Saluki"],
        ["2025-06-14 21:00", "ZOLOTO"],
        ["2025-06-14 22:40", "АРИЯ"],
        ["2025-06-15 12:00", "СмешBand"],
        ["2025-06-15 13:00", "Мультfильмы"],
        ["2025-06-15 14:00", "obraza net"],
        ["2025-06-15 15:00", "Пётр Налич"],
        ["2025-06-15 16:00", "мытищи в огне"],
        ["2025-06-15 17:00", "Базар"],
        ["2025-06-15 18:00", "The Hatters"]
    ],
    "TITANA": [
        ["2025-06-13 16:00", "Baby Cute"],
        ["2025-06-13 16:40", "Пальцева Экспириенс"],
        ["2025-06-13 17:40", "Людмил Огурченко"],
        ["2025-06-13 18:40", "Бюро"],
        ["2025-06-13 19:40", "OLIGARKH"],
        ["2025-06-13 20:40", "Yan Dilan"],
        ["2025-06-13 21:50", "Конец солнечных дней"],
        ["2025-06-14 00:30", "The OM"],
        ["2025-06-14 12:00", "Три Вторых"],
        ["2025-06-14 12:50", "El Mashe"],
        ["2025-06-14 13:40", "Inna Syberia"],
        ["2025-06-14 14:40", "Остыл"],
        ["2025-06-14 15:40", "Manapart"],
        ["2025-06-14 16:40", "Juzeppe Junior"],
        ["2025-06-14 17:40", "Манго буст"],
        ["2025-06-14 18:40", "Хмыров"],
        ["2025-06-14 19:40", "Стрио"],
        ["2025-06-14 20:40", "Молодость внутри"],
        ["2025-06-14 21:50", "Лолита косс"],
        ["2025-06-15 00:30", "Бонд с кнопкой"],
        ["2025-06-15 12:20", "Хохма"],
        ["2025-06-15 13:20", "Cardio killer"],
        ["2025-06-15 14:20", "Можем хуже"],
        ["2025-06-15 15:20", "Breaking system"],
        ["2025-06-15 16:20", "Stigmata"],
        ["2025-06-15 17:20", "Jane air"]
    ],
    "Маяк": [
        ["2025-06-13 15:20", "HIDeout"],
        ["2025-06-13 16:20", "Rofman"],
        ["2025-06-13 17:20", "Koledova"],
        ["2025-06-13 18:20", "Без обид"],
        ["2025-06-13 19:20", "Антон прокофьев"],
        ["2025-06-13 20:20", "Синдром главного героя"],
        ["2025-06-13 21:50", "собачий lie"],
        ["2025-06-14 12:20", "tabasco band"],
        ["2025-06-14 13:20", "мама не узнает"],
        ["2025-06-14 14:20", "brodsky"],
        ["2025-06-14 15:20", "lithium"],
        ["2025-06-14 16:20", "Дедовский свитер"],
        ["2025-06-14 17:20", "Давай"],
        ["2025-06-14 18:20", "Uncle pecos"],
        ["2025-06-14 19:20", "Rasputniki"],
        ["2025-06-14 20:20", "Melekess"],
        ["2025-06-14 21:50", "Monolyt (IL)"],
        ["2025-06-15 11:40", "Mazzltoff"],
        ["2025-06-15 12:40", "Дисциплина безбольной биты"],
        ["2025-06-15 13:40", "Ник брусковский"],
        ["2025-06-15 14:40", "Рубеж веков"],
        ["2025-06-15 15:40", "Каспий"],
        ["2025-06-15 16:40", "kamilla robertovna"]
    ],
    "Дачный клуб Т-Банк": [
        ["2025-06-13 13:00", "Costa Dorada"],
        ["2025-06-13 15:00", "Крими Край"],
        ["2025-06-13 17:00", "Я Софа"],
        ["2025-06-13 19:00", "Nice City"],
        ["2025-06-13 21:00", "Runa Project"],
        ["2025-06-13 22:00", "соня хочет танцевать"],
        ["2025-06-13 02:00", "Breakpillzz"],
        ["2025-06-14 13:00", "Летяга"],
        ["2025-06-14 15:00", "Клуб 33"],
        ["2025-06-14 17:00", "Polina Offline"],
        ["2025-06-14 19:00", "КОМНАТА105"],
        ["2025-06-14 21:00", "не вижу"],
        ["2025-06-14 22:00", "SHAMAN IVAN"],
        ["2025-06-14 00:00", "Ielele"],
        ["2025-06-14 02:00", "ParadigmA"],
        ["2025-06-15 13:00", "Пилс"],
        ["2025-06-15 15:00", "Гнев господень"],
        ["2025-06-15 17:00", "Лучший самый день"],
        ["2025-06-15 20:00", "Gokk’n’Tony"]
    ],
    "Амбар «ARTИСТ»": [
        ["2025-06-13 23:00", "Lowriderz"],
        ["2025-06-13 23:00", "Despersion"],
        ["2025-06-13 23:00", "Impish"],
        ["2025-06-13 23:00", "Ryan Audley"],
        ["2025-06-13 23:00", "Matyo"],
        ["2025-06-14 23:00", "ТРАВМА"],
        ["2025-06-14 23:00", "Lion (SLK)"],
        ["2025-06-14 23:00", "UNKNOWN ARTISTS"]
    ],
    "VASHANA АРЕНА": [
        ["2025-06-13 11:30", "DJ PERETSE"],
        ["2025-06-13 12:00", "DJ-сеты"],
        ["2025-06-13 17:00", "LIRA"],
        ["2025-06-13 17:30", "DJ-сеты"],
        ["2025-06-13 22:00", "SAINT RIDER"],
        ["2025-06-13 23:00", "DJ FEEL"],
        ["2025-06-14 11:30", "DJ-сет"],
        ["2025-06-14 12:00", "KOROLEV"],
        ["2025-06-14 12:30", "DJ-сеты"],
        ["2025-06-14 16:00", "M.PRAVDA"],
        ["2025-06-14 16:30", "DJ-сеты"],
        ["2025-06-14 18:30", "ANDROID"],
        ["2025-06-14 19:00", "DJ-сеты"],
        ["2025-06-14 22:00", "DJ BOYKO"],
        ["2025-06-14 23:00", "PROFIT"],
        ["2025-06-15 12:00", "SECRET GUEST"],
        ["2025-06-15 12:00", "DJ-сеты"],
        ["2025-06-15 16:30", "SOROKOVA"],
        ["2025-06-15 17:00", "AKS"],
        ["2025-06-15 17:30", "SECRET GUEST"]
    ],
    "Детская сцена Ариэль": [
        ["2025-06-13 14:00", "Скверная Участь"],
        ["2025-06-13 14:15", "Децебелки"],
        ["2025-06-13 14:30", "Атомы"],
        ["2025-06-13 14:45", "Япония"],
        ["2025-06-13 15:00", "Варианты"],
        ["2025-06-13 15:15", "Грозные Завры"],
        ["2025-06-13 15:30", "Хром"],
        ["2025-06-13 15:45", "Послезавтра"],
        ["2025-06-13 16:00", "Меньше Чем Три"],
        ["2025-06-13 16:15", "Искры Безумия"],
        ["2025-06-13 16:30", "Что с лицом?"],  
        ["2025-06-13 16:45", "Рок и точка"],  
        ["2025-06-13 17:15", "Саша Кучеряша"],  
        ["2025-06-13 17:30", "Клондайк"],  
        ["2025-06-13 17:45", "По Тормозам"],  
        ["2025-06-13 18:00", "Твердый знакЪ"],  
        ["2025-06-13 18:15", "AV"],  
        ["2025-06-13 18:30", "Мамины Нервы"],  
        ["2025-06-13 18:45", "Синдром Дефицита"],  
        ["2025-06-13 19:00", "До Вечера"],  
        ["2025-06-13 19:15", "Супернова"],  
        ["2025-06-13 19:30", "Мы придумаем"],  
        ["2025-06-13 19:45", "Электра"],  
        ["2025-06-14 10:00", "Тигры"],  
        ["2025-06-14 10:15", "ВикоДин"],  
        ["2025-06-14 10:30", "Оптимисты синергия"],  
        ["2025-06-14 10:45", "Дети Аиста"],  
        ["2025-06-14 11:00", "Метроном синергия"],  
        ["2025-06-14 11:15", "Тигры"],  
        ["2025-06-14 11:30", "Рок-макароны"],  
        ["2025-06-14 11:45", "Чикен рок"],  
        ["2025-06-14 12:00", "Децебелки"],  
        ["2025-06-14 12:15", "Скверная участь"],  
        ["2025-06-14 12:30", "Мяу Теоры"],  
        ["2025-06-14 12:45", "ДЕТСКОЕ РАДИО — конкурсы"],  
        ["2025-06-14 13:15", "Platanos Band"],  
        ["2025-06-14 13:45", "Спички"],  
        ["2025-06-14 14:15", "Super Детки"],  
        ["2025-06-14 15:15", "Bamboo"],  
        ["2025-06-14 15:45", "Атомы"],  
        ["2025-06-14 16:15", "Bumbles"],  
        ["2025-06-14 16:30", "VыSTREL"],  
        ["2025-06-14 17:00", "По Тормозам"],  
        ["2025-06-14 17:45", "Мила Новак и Сергей Зауэрс"],  
        ["2025-06-14 18:00", "Чудо"],  
        ["2025-06-14 18:15", "Подарочки"],  
        ["2025-06-14 18:30", "Япония"],  
        ["2025-06-14 18:45", "Острые углы"],  
        ["2025-06-14 19:00", "Metal Forest"],  
        ["2025-06-14 19:15", "Inflorescence"],  
        ["2025-06-15 10:30", "Супернова"],  
        ["2025-06-15 10:45", "Электра"],  
        ["2025-06-15 11:00", "Скверная участь"],  
        ["2025-06-15 11:15", "Деловой Вопрос"],  
        ["2025-06-15 11:30", "Пылинки синергия"],  
        ["2025-06-15 11:45", "Ядерные Осадки"],  
        ["2025-06-15 12:00", "Самонаводяшие Собаки"],  
        ["2025-06-15 12:15", "3000 причин синергия"],  
        ["2025-06-15 13:00", "Атмосфера BM"],  
        ["2025-06-15 13:15", "Grass-hoppers"],  
        ["2025-06-15 13:30", "Рок-Мотор"],  
        ["2025-06-15 13:45", "Электрочайник"],  
        ["2025-06-15 14:00", "Sound Waves"],  
        ["2025-06-15 14:15", "Forgotten years"],  
        ["2025-06-15 14:30", "Меланхолия под кожей"],  
        ["2025-06-15 14:45", "Казантип"],  
        ["2025-06-15 15:00", "Спаркс"],  
        ["2025-06-15 15:15", "Поколение"],  
        ["2025-06-15 15:30", "Атомы"],  
        ["2025-06-15 15:45", "Япония"],  
        ["2025-06-15 16:00", "Metallforest"],  
        ["2025-06-15 16:15", "Чикен рок"],  
        ["2025-06-15 16:30", "Викодин"]  
      ]  
}

SCENES = load_json(SCENES_FILE, DEFAULT_SCENES)
FAVS   = load_json(FAVS_FILE, {})

user_context = {}

# ====== Клавиатуры ======
def main_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Открытие дверей", "Обмен билетов")
    kb.row("Расписание Сцен", "⭐ Избранное")
    kb.row("Инфоцентр / Касса / Камеры хранения", "Душевые и зоны кипятка")
    kb.row("Карта фестиваля", "Развлечения на фестивале")
    kb.row("FAQ")
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

# ====== Тексты FAQ и разделов ======
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
        "Yan Dilan, Бюро, МОЛОДОСТЬ ВНУТРИ, Пальцева Экспириенс, Людмил Огурченко, Breaking System, Brodsky, "
        "uncle pecos, Стрио, соня хочет танцевать, Juzeppe Junior, Лолита Косс, Остыл, Melekess, El Mashe, "
        "Дедовский Свитер, Baby Cute, Антон Прокофьев, Breakpillzz, Мама не узнает, GOKK’N’TONY, Можем хуже, "
        "RASPUTНIKI (KZ), Inna Syberia, без обид, Давай, LITHIUM, Каспий, Три вторых, Рубеж Веков, "
        "синдром главного героя, Koledova, я Софа, Mazzltoff, ielele, Polina Offline, Ник Брусковский, ROFMAN, "
        "летяга, Tabasco Band, Гнев Господень, Дисциплина безбольной биты, Hideout, Савелiчъ Бэнд, ParadigmA, "
        "Клуб 33 и другие, новые анонсы каждую неделю!\n\n"
        "«Дикая Мята» по праву считается самым комфортным опен-эйром страны. Организованная парковка, "
        "бесплатная питьевая вода и душевые с горячей водой, дорожки, выложенные тротуарной плиткой, "
        "освещенные палаточные кемпинги, которые размечены на улицы и индивидуальные места под палатки, "
        "комната матери и ребенка, бассейн, видовой ресторан и арт-амбар, sup-станция и лаундж-зоны.\n\n"
        "Фудкорт фестиваля предлагает кухни мира на любой вкус и кошелек, вегетарианскую зону и атмосферную "
        "перголу с блюдами от шеф-поваров.\n\n"
        "Также для гостей представлено множество развлечений:\n"
        "— В пространстве Green Age проходят йога-практики, экстатик дэнс, арт-медитации, мастер-классы "
        "по нейрографике и лекции о здоровом образе жизни.\n"
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

# ====== Вспомогательная функция: получить расписание по дате ======
def get_entries_for_date(scene: str, iso_date: str):
    date_dt = datetime.fromisoformat(f"{iso_date} 00:00")
    next_dt = date_dt + timedelta(days=1)
    result = []
    for tstr, artist in SCENES.get(scene, []):
        dt = datetime.fromisoformat(tstr)
        if dt.date() == date_dt.date() or (dt.date() == next_dt.date() and dt.time() < dtime(2, 0)):
            result.append((tstr, artist))
    return result

# ====== Фоновая задача: проверка избранного и отправка уведомлений ======
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

@dp.message_handler(lambda m: m.text == "Открытие дверей")
async def info_open_doors(msg: types.Message):
    # Замените текст ниже на актуальную информацию
    text = "Двери открываются в 18:00 12 июня."
    await msg.reply(text, reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "Обмен билетов")
async def info_ticket_exchange(msg: types.Message):
    # Используем ранее заданный FAQ-текст «Обмен билетов на браслеты»
    await msg.reply(FAQ_TEXTS["Обмен билетов на браслеты"], reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "Инфоцентр / Касса / Камеры хранения")
async def info_info_center(msg: types.Message):
    # Замените текст ниже на актуальную информацию
    text = (
        "Инфоцентр, касса и камеры хранения находятся у входа. "
        "Часы работы: с 08:00 до 23:00.\n"
        "Адрес кассы: главный вход фестиваля.\n"
        "Камеры хранения платные, принимают багаж и снаряжение."
    )
    await msg.reply(text, reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "Душевые и зоны кипятка")
async def info_showers_boiling(msg: types.Message):
    # Объединяем два FAQ-текста
    text = (
        f"{FAQ_TEXTS['Расписание работы душевых']}\n\n"
        f"{FAQ_TEXTS['Расписание зон с кипятком']}"
    )
    await msg.reply(text, reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "Карта фестиваля")
async def info_map(msg: types.Message):
    # Используем ранее заданный FAQ-текст «Карта Фестиваля»
    await msg.reply(FAQ_TEXTS["Карта Фестиваля"], reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "Развлечения на фестивале")
async def info_entertainment(msg: types.Message):
    # Замените текст ниже на актуальный список развлечений
    text = (
        "— В пространстве Green Age: йога, арт-медитации, экстатик дэнс, "
        "лекции о здоровом образе жизни.\n"
        "— Бьюти-зона: брайдинг, макияж, барбершоп.\n"
        "— Территория детства: карусели, аттракционы, мастер-классы, "
        "детская сцена «Ариэль».\n"
        "— Фестивальная ярмарка: хэндмейд, авторская одежда и аксессуары.\n"
        "— Спортивная площадка: воркаут-зона, турниры по пляжному волейболу.\n"
        "— Призовые активности от партнеров и лаундж-зоны для отдыха."
    )
    await msg.reply(text, reply_markup=main_menu_kb())

@dp.message_handler(lambda m: m.text == "FAQ")
async def cmd_faq(msg: types.Message):
    await msg.reply("❓ FAQ — выберите тему:", reply_markup=faq_kb())

@dp.message_handler(lambda m: m.text in FAQ_TEXTS)
async def faq_answer(msg: types.Message):
    await msg.reply(FAQ_TEXTS[msg.text], reply_markup=faq_kb())

@dp.message_handler(lambda m: m.text == "Расписание Сцен")
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
    await msg.reply("📋 Ваше избранное:\n" + "\n".join(lines), reply_markup=main_menu_kb())

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
    for idx, (tstr, artist) in enumerate(entries):
        kb.add(InlineKeyboardButton(f"{tstr[11:16]} — {artist}", callback_data=f"fav|{scene}|{iso}|{idx}"))
    await msg.reply(f"Расписание «{scene}» на {msg.text}:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("fav|"))
async def cb_fav(cq: types.CallbackQuery):
    _, scene, iso, idx = cq.data.split("|", 3)
    idx = int(idx)
    tstr, artist = get_entries_for_date(scene, iso)[idx]
    uid = str(cq.from_user.id)
    FAVS.setdefault(uid, [])
    entry = {"scene": scene, "time": tstr, "artist": artist, "notified": False}
    if not any(x["scene"] == scene and x["time"] == tstr for x in FAVS[uid]):
        FAVS[uid].append(entry)
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
    SCENES[scene].append([dt_str, artist])
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
    entry = [dt_str, artist]
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
