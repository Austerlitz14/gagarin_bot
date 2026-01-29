from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.text_decorations import html_decoration as hd

from keyboards import back_to_menu_kb

router = Router()

def h(text: str) -> str:
    return hd.quote(text or "")

@router.callback_query(lambda c: c.data == "menu:links")
async def menu_links(callback: CallbackQuery, json_handler):
    links = await json_handler.get_common_links()

    if not links:
        text = "Пока нет общих ссылок. Админ может добавить через /add_common_link Название | https://..."
        await callback.message.edit_text(h(text), reply_markup=back_to_menu_kb())
        await callback.answer()
        return

    lines = []
    for l in links:
        title = h(l.get("title", "Ссылка"))
        url = l.get("url", "").strip()
        if url:
            lines.append(f"• <a href='{url}'>{title}</a>")
        else:
            lines.append(f"• {title}")

    text = "🔗 <b>Ссылки</b>\n\n" + "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()

@router.callback_query(lambda c: c.data == "menu:about")
async def menu_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ <b>Князь Гагарин</b>\n\n"
        "Бот про студенческое сообщество волонтёров, которые зимой выезжают в деревни.\n"
        "Тут можно смотреть фото по годам, читать историю и находить ссылки.\n",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()
