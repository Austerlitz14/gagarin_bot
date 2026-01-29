from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu_kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я бот «Князь Гагарин».\n"
        "Выбирай раздел ниже:",
        reply_markup=main_menu_kb(),
    )

@router.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Твой id: <code>{message.from_user.id}</code>")

@router.callback_query(lambda c: c.data == "nav:menu")
async def nav_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбирай раздел ниже:",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
