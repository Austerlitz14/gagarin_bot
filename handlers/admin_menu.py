from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards import admin_menu_kb, back_to_menu_kb

router = Router()

def _is_admin_cb(cb: CallbackQuery, admin_ids: set[int]) -> bool:
    return cb.from_user and cb.from_user.id in admin_ids

@router.callback_query(lambda c: c.data == "menu:admin")
async def open_admin_menu(callback: CallbackQuery, admin_ids):
    if not _is_admin_cb(callback, admin_ids):
        # тихо игнорируем
        await callback.answer()
        return

    await callback.message.edit_text(
        "⚙️ <b>Управление</b>\nВыбери действие:",
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()

@router.callback_query(lambda c: (c.data or "").startswith("admin:"))
async def admin_action_help(callback: CallbackQuery, admin_ids):
    if not _is_admin_cb(callback, admin_ids):
        await callback.answer()
        return

    action = callback.data.split(":", 1)[1]

    helps = {
        "add_photo": (
            "🖼 <b>Добавить фото</b>\n\n"
            "1) Напиши: <code>/add_photo 2024</code>\n"
            "2) Отправь фотографии (можно пачкой)\n"
            "3) Заверши: <code>/done</code>"
        ),
        "set_info": (
            "ℹ️ <b>Задать инфо года</b>\n\n"
            "Пример:\n<code>/set_info 2024 Короткое описание выезда</code>"
        ),
        "add_link": (
            "🔗 <b>Добавить ссылку года</b>\n\n"
            "Пример:\n<code>/add_link 2024 Группа ВК | https://vk.com/...</code>"
        ),
        "set_history": (
            "📜 <b>Обновить историю</b>\n\n"
            "Пример:\n<code>/set_history Текст истории...</code>"
        ),
        "add_common_link": (
            "🔗 <b>Добавить общую ссылку</b>\n\n"
            "Пример:\n<code>/add_common_link Чат | https://t.me/...</code>"
        ),
    }

    text = helps.get(action, "Неизвестное действие.")
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()
