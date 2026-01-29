from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards import main_menu_kb

router = Router()

def is_admin_id(user_id: int, admin_ids: set[int]) -> bool:
    return user_id in admin_ids

@router.message(CommandStart())
async def start(message: Message, admin_ids):
    admin = is_admin_id(message.from_user.id, admin_ids)
    await message.answer(
        "👋 Привет! Князь Гагарин на связи!\nВыбирай раздел ниже:",
        reply_markup=main_menu_kb(is_admin=admin),
    )

@router.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Твой id: <code>{message.from_user.id}</code>")

@router.callback_query(lambda c: c.data == "nav:menu")
async def nav_menu(callback: CallbackQuery, admin_ids):
    admin = is_admin_id(callback.from_user.id, admin_ids)
    await callback.message.edit_text(
        "Выбирай раздел ниже:",
        reply_markup=main_menu_kb(is_admin=admin),
    )
    await callback.answer()
