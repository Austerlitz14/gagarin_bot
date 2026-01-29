from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb(is_admin: bool = False):
    kb = InlineKeyboardBuilder()
    kb.button(text="📷 Фото по годам", callback_data="menu:photos")
    kb.button(text="📜 История", callback_data="menu:history")
    kb.button(text="🔗 Ссылки", callback_data="menu:links")
    kb.button(text="ℹ️ О сообществе", callback_data="menu:about")
    if is_admin:
        kb.button(text="⚙️ Управление", callback_data="menu:admin")
        kb.adjust(2, 2, 1)
    else:
        kb.adjust(2, 2)
    return kb.as_markup()

def back_to_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ В меню", callback_data="nav:menu")
    return kb.as_markup()

def years_kb(years: list[int]):
    kb = InlineKeyboardBuilder()
    if not years:
        kb.button(text="⬅️ В меню", callback_data="nav:menu")
        return kb.as_markup()

    for y in years:
        kb.button(text=str(y), callback_data=f"year:{y}")

    kb.adjust(4)
    kb.button(text="⬅️ В меню", callback_data="nav:menu")
    return kb.as_markup()

def year_actions_kb(year: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🖼 Показать фото", callback_data=f"yearphotos:{year}")
    kb.button(text="ℹ️ Инфо выезда", callback_data=f"yearinfo:{year}")
    kb.button(text="🔗 Ссылки этого года", callback_data=f"yearlinks:{year}")
    kb.button(text="⬅️ К годам", callback_data="nav:years")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def admin_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🖼 Добавить фото за год", callback_data="admin:add_photo")
    kb.button(text="ℹ️ Задать инфо года", callback_data="admin:set_info")
    kb.button(text="🔗 Добавить ссылку года", callback_data="admin:add_link")
    kb.button(text="📜 Обновить историю", callback_data="admin:set_history")
    kb.button(text="🔗 Добавить общую ссылку", callback_data="admin:add_common_link")
    kb.button(text="⬅️ В меню", callback_data="nav:menu")
    kb.adjust(1, 1, 1, 1, 1, 1)
    return kb.as_markup()
