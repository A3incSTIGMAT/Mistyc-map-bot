# main.py
import os
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

# Получаем токен из переменной окружения (никогда не хардкодим!)
print(f"✅ BOT_TOKEN: {os.getenv('BOT_TOKEN')}")
if not BOT_TOKEN:
    raise RuntimeError("❌ Переменная BOT_TOKEN не задана! Добавьте её в Render или .env")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("✨ Привет! Отправь дату рождения в формате ДД.ММ.ГГГГ")

@router.message()
async def handle_date(message: Message):
    text = message.text.strip()
    if len(text) == 10 and text[2] == '.' and text[5] == '.':
        digits = [int(c) for c in text if c.isdigit()]
        life_path = sum(digits)
        while life_path > 9 and life_path not in (11, 22, 33):
            life_path = sum(int(d) for d in str(life_path))
        await message.answer(f"🔮 Твоё Число Судьбы: {life_path}")
    else:
        await message.answer("Пожалуйста, введи дату в формате ДД.ММ.ГГГГ")

dp.include_router(router)

async def main():
    print("✅ Бот запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
