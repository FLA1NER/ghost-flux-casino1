import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import aiohttp
import json

from database import get_user, create_user

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 5450857649  # Ваш ID

bot = Bot(token=BOT_TOKEN)
router = Router()

# Клавиатура с Mini App
def get_main_keyboard():
    web_app = WebAppInfo(url="https://your-username.github.io/GhostFlux-Casino/mini_app/")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Открыть Казино", web_app=web_app)],
            [KeyboardButton(text="ℹ️ Помощь"), KeyboardButton(text="📊 Мой профиль")]
        ],
        resize_keyboard=True
    )
    return keyboard

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    await create_user(user.id, user.username)
    
    welcome_text = (
        "👻 Добро пожаловать в **Ghost FluX Casino**!\n\n"
        "🎰 Используй кнопку ниже, чтобы открыть казино и начать играть!\n"
        "⭐️ Выигрывай подарки, открывай кейсы и крути рулетку!\n\n"
        "💎 Наш канал: https://t.me/Ghost_FluX"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(F.text == "📊 Мой профиль")
async def show_profile(message: Message):
    """Показать профиль пользователя"""
    user_data = await get_user(message.from_user.id)
    if user_data:
        profile_text = (
            f"👤 **Ваш профиль**\n"
            f"🆔 ID: `{user_data['user_id']}`\n"
            f"⭐️ Баланс: **{user_data['balance']}** звезд\n"
            f"🎁 Подарков в инвентаре: **{len(user_data['inventory'])}**\n\n"
            f"💎 Для пополнения баланса обращайтесь к @KXKXKXKXKXKXKXKXKXKXK"
        )
        await message.answer(profile_text)
    else:
        await message.answer("Профиль не найден. Используйте /start")

@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    """Показать справку"""
    help_text = (
        "🎰 **Ghost FluX Casino - Помощь**\n\n"
        "⭐️ **Звезды** - валюта казино\n"
        "🎁 **Подарки** - можно выводить или продавать\n\n"
        "**Режимы игр:**\n"
        "• 🎁 **Gift Box** (25 звезд) - кейс с подарками\n"
        "• 🎡 **Ghost Roulette** (50 звезд) - рулетка с шансом на NFT\n"
        "• 🎯 **Бонусный кейс** - бесплатно каждые 24 часа\n\n"
        "💎 **Наш канал:** https://t.me/Ghost_FluX\n"
        "👨‍💻 **Поддержка:** @KXKXKXKXKXKXKXKXKXKXK"
    )
    await message.answer(help_text)