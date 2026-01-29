from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards import back_to_menu_kb

router = Router()

@router.callback_query(lambda c: c.data == "menu:history")
async def menu_history(callback: CallbackQuery, json_handler):
    text = await json_handler.get_history()
    if not text:
        text = "История пока не заполнена. Админ может задать через /set_history <текст>."
    await callback.message.edit_text(f"📜 <b>История</b>\n\n{text}", reply_markup=back_to_menu_kb())
    await callback.answer()
