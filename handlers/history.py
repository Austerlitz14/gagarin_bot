from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.text_decorations import html_decoration as hd

from keyboards import back_to_menu_kb

router = Router()

def h(text: str) -> str:
    return hd.quote(text or "")

@router.callback_query(lambda c: c.data == "menu:history")
async def menu_history(callback: CallbackQuery, json_handler):
    text = await json_handler.get_history()
    if not text:
        text = "История пока не заполнена."
    await callback.message.edit_text(
        f"📜 <b>История</b>\n\n{h(text)}",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()
