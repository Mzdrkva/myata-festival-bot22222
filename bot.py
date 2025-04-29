import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

ARTISTS = ["Artur", "Katya", "Masha", "Sergey"]
DATA_FILE = "user_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Привет! Напиши /choose, чтобы выбрать любимых артистов.")

@dp.message_handler(commands=['choose'])
async def choose_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(artist, callback_data=artist) for artist in ARTISTS]
    keyboard.add(*buttons)
    await message.reply("Выбери артистов:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ARTISTS)
async def callback_handler(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    artist = callback_query.data
    data = load_data()
    if user_id not in data:
        data[user_id] = []
    if artist not in data[user_id]:
        data[user_id].append(artist)
        save_data(data)
        await bot.answer_callback_query(callback_query.id, f"{artist} добавлен в избранное!")
    else:
        await bot.answer_callback_query(callback_query.id, f"{artist} уже в избранном.")

@dp.message_handler(commands=['myartists'])
async def myartists_cmd(message: types.Message):
    user_id = str(message.from_user.id)
    data = load_data()
    artists = data.get(user_id, [])
    if artists:
        await message.reply("Ваши избранные артисты:\n" + "\n".join(f"• {a}" for a in artists))
    else:
        await message.reply("Вы пока не выбрали артистов. Напиши /choose")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
