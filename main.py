# main.py
import os
import random
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, LabeledPrice
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# === ИНИЦИАЛИЗАЦИЯ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ Переменная BOT_TOKEN не задана! Добавьте её в Render.")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# Простая "база" в памяти (для демо)
referrals = {}  # user_id → referrer_id
balances = {}   # user_id → balance_in_stars

# Таро-карты (22 главных аркана)
TAROT_CARDS = [
    "Шут", "Маг", "Жрица", "Императрица", "Император", "Жрец", "Влюбленные",
    "Колесница", "Сила", "Отшельник", "Колесо Фортуны", "Справедливость",
    "Повешенный", "Смерть", "Умеренность", "Дьявол", "Башня", "Звезда",
    "Луна", "Солнце", "Суд", "Мир"
]

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔮 Нумерология")
    builder.button(text="🃏 Таро дня")
    builder.button(text="👥 Пригласить друга")
    builder.button(text="💳 Купить услугу")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_buy_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Нумерология (299 ₽)")
    builder.button(text="Таро (199 ₽)")
    builder.button(text="Натальная карта (499 ₽)")
    builder.button(text="🏠 В меню")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# === ОСНОВНЫЕ ОБРАБОТЧИКИ ===
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Обработка реферальной ссылки
    if len(args) > 1 and args[1].startswith("ref"):
        try:
            ref_id = int(args[1][3:])
            if ref_id != user_id:  # нельзя пригласить самого себя
                referrals[user_id] = ref_id
                balances[ref_id] = balances.get(ref_id, 0) + 5
                await message.answer("✨ Ты пришёл по рефералке! Реферер получил +5 ⭐", reply_markup=get_main_menu())
                return
        except ValueError:
            pass
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! ✨\n"
        "Отправь дату рождения (ДД.ММ.ГГГГ), и я раскрою твой код души!",
        reply_markup=get_main_menu()
    )

@router.message(F.text.regexp(r"\d{2}\.\d{2}\.\d{4}"))
async def handle_birth_date(message: Message):
    date_str = message.text.strip()
    digits = [int(c) for c in date_str if c.isdigit()]
    life_path = sum(digits)
    while life_path > 9 and life_path not in (11, 22, 33):
        life_path = sum(int(d) for d in str(life_path))
    
    tarot_card = TAROT_CARDS[int(date_str.split(".")[0]) % 22]
    
    await message.answer(
        f"✨ <b>Число Судьбы:</b> {life_path}\n"
        f"🃏 <b>Аркан Таро:</b> {tarot_card}",
        reply_markup=get_buy_menu()
    )

# === КНОПКИ МЕНЮ ===
@router.message(F.text == "🔮 Нумерология")
async def numerology(message: Message):
    await message.answer("Отправь дату рождения — получишь число судьбы!")

@router.message(F.text == "🃏 Таро дня")
async def taro_day(message: Message):
    card = random.choice(TAROT_CARDS)
    await message.answer(f"✨ Твой аркан сегодня: <b>{card}</b>")

@router.message(F.text == "👥 Пригласить друга")
async def referral(message: Message):
    ref_link = f"https://t.me/CosmoSoulBot?start=ref{message.from_user.id}"
    balance = balances.get(message.from_user.id, 0)
    await message.answer(
        f"🌟 Твоя ссылка:\n{ref_link}\n\n"
        f"💰 Баланс: {balance} ⭐"
    )

@router.message(F.text == "💳 Купить услугу")
async def buy_service(message: Message):
    await message.answer("Выбери услугу:", reply_markup=get_buy_menu())

@router.message(F.text == "🏠 В меню")
async def back_to_menu(message: Message):
    await cmd_start(message)

# === ОПЛАТА (Telegram Stars) ===
@router.message(F.text == "Нумерология (299 ₽)")
async def buy_numerology(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Нумерология",
        description="Полный нумерологический портрет",
        prices=[LabeledPrice(label="Услуга", amount=299)],
        provider_token="",  # ← пусто для Stars!
        payload="numerology_1",
        currency="XTR",
        start_parameter="numerology"
    )

@router.message(F.text == "Таро (199 ₽)")
async def buy_taro(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Таро",
        description="Персональный расклад",
        prices=[LabeledPrice(label="Услуга", amount=199)],
        provider_token="",
        payload="taro_1",
        currency="XTR",
        start_parameter="taro"
    )

@router.message(F.text == "Натальная карта (499 ₽)")
async def buy_natal(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Натальная карта",
        description="Полная астрологическая карта",
        prices=[LabeledPrice(label="Услуга", amount=499)],
        provider_token="",
        payload="natal_1",
        currency="XTR",
        start_parameter="natal"
    )

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    referrer_id = referrals.get(user_id)
    if referrer_id:
        balances[referrer_id] = balances.get(referrer_id, 0) + 15
        try:
            await bot.send_message(referrer_id, "🎉 Твой друг купил услугу! Ты получил +15 ⭐ бонуса!")
        except:
            pass  # игнорируем, если пользователь заблокировал бота
    await message.answer("✅ Спасибо за покупку! Твой заказ обрабатывается.")

# === ЗАПУСК БОТА ===
async def main():
    dp.include_router(router)
    print("🚀 Бот запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        raise
