# main.py
import os
import random
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Инициализация
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ Переменная BOT_TOKEN не задана! Добавьте её в Render или .env")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# База данных (упрощённая — в памяти)
referrals = {}  # {user_id: referrer_id}
balances = {}   # {user_id: balance_in_stars}

# Таро-карты
TAROT_CARDS = [
    "Шут", "Маг", "Жрица", "Императрица", "Император", "Жрец", "Влюбленные",
    "Колесница", "Сила", "Отшельник", "Колесо Фортуны", "Справедливость",
    "Повешенный", "Смерть", "Умеренность", "Дьявол", "Башня", "Звезда",
    "Луна", "Солнце", "Суд", "Мир"
]

# Главное меню
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔮 Нумерология")
    builder.button(text="🃏 Таро дня")
    builder.button(text="👥 Пригласить друга")
    builder.button(text="💳 Купить услугу")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Обработчик /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref"):
        ref_id = args[1][3:]  # "ref123" → "123"
        referrals[message.from_user.id] = int(ref_id)
        balances.setdefault(ref_id, 0)
        balances[ref_id] += 5  # бонус за приглашение
        await message.answer(f"✨ Ты пришёл по рефералке от {ref_id}! Получи +5 ⭐ бонуса!", reply_markup=get_main_menu())
    else:
        await message.answer(
            f"Привет, {message.from_user.first_name}! ✨\n"
            "Я — твой персональный эзотерик в Telegram.\n"
            "Отправь дату рождения (например: 29.04.1964), и я раскрою твой код души!",
            reply_markup=get_main_menu()
        )

# Обработка даты рождения
@router.message(F.text.regexp(r"\d{2}\.\d{2}\.\d{4}"))
async def handle_birth_date(message: Message):
    date_str = message.text.strip()
    digits = [int(c) for c in date_str if c.isdigit()]
    life_path = sum(digits)
    while life_path > 9 and life_path not in (11, 22, 33):
        life_path = sum(int(d) for d in str(life_path))

    tarot_card = TAROT_CARDS[int(date_str.split(".")[0]) % 22]

    await message.answer(
        f"✨ <b>Твой Число Судьбы:</b> {life_path}\n"
        f"🃏 <b>Твой Аркан Таро:</b> {tarot_card}\n\n"
        "Хочешь <b>полный разбор</b>?\n"
        "👉 Нажми ниже:"
    )
    kb = ReplyKeyboardBuilder()
    kb.button(text="Нумерология (299 ₽)")
    kb.button(text="Таро (199 ₽)")
    kb.button(text="Натальная карта (499 ₽)")
    kb.button(text="🏠 В меню")
    kb.adjust(2)
    await message.answer("Выбери услугу:", reply_markup=kb.as_markup(resize_keyboard=True))

# Обработчики кнопок
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
    await message.answer(
        f"🌟 Пригласи друга по ссылке:\n{ref_link}\n\n"
        "Когда он купит услугу — ты получишь 15% на баланс!\n"
        f"Твой текущий баланс: {balances.get(message.from_user.id, 0)} ⭐"
    )

@router.message(F.text == "💳 Купить услугу")
async def buy_service(message: Message):
    await message.answer("Выбери услугу для оплаты:", reply_markup=get_buy_menu())

def get_buy_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Нумерология (299 ₽)")
    builder.button(text="Таро (199 ₽)")
    builder.button(text="Натальная карта (499 ₽)")
    builder.button(text="🏠 В меню")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Оплата
@router.message(F.text == "Нумерология (299 ₽)")
async def buy_numerology(message: Message):
    prices = [LabeledPrice(label="Нумерологический портрет", amount=299)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Нумерология",
        description="Полный нумерологический портрет вашей личности",
        prices=prices,
        provider_token="",  # ← пусто для Stars!
        payload="numerology_1",
        currency="XTR",
        start_parameter="numerology"
    )

@router.message(F.text == "Таро (199 ₽)")
async def buy_taro(message: Message):
    prices = [LabeledPrice(label="Расклад Таро", amount=199)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Таро",
        description="Персональный расклад на любую ситуацию",
        prices=prices,
        provider_token="",  # ← пусто для Stars!
        payload="taro_1",
        currency="XTR",
        start_parameter="taro"
    )

@router.message(F.text == "Натальная карта (499 ₽)")
async def buy_natal(message: Message):
    prices = [LabeledPrice(label="Натальная карта", amount=499)]
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Натальная карта",
        description="Полная астрологическая карта с интерпретацией",
        prices=prices,
        provider_token="",  # ← пусто для Stars!
        payload="natal_1",
        currency="XTR",
        start_parameter="natal"
    )

@router.message(F.text == "🏠 В меню")
async def back_to_menu(message: Message):
    await cmd_start(message)

# Обработчик платежей
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    # Увеличиваем баланс реферера (если есть)
    referrer_id = referrals.get(user_id)
    if referrer_id:
        balances.setdefault(referrer_id, 0)
        balances[referrer_id] += 15  # 15% от 100 = 15 ⭐ (можно изменить)
        await bot.send_message(referrer_id, f"🎉 Твой друг купил услугу! Ты получил +15 ⭐ бонус")
