from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.text_decorations import html_decoration as hd

from keyboards import years_kb, year_actions_kb

def h(text: str) -> str:
    # Экранирует < > & чтобы ParseMode.HTML не ломался
    return hd.quote(text or "")

def _chunk(lst, size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

router = Router()

@router.callback_query(lambda c: c.data == "menu:photos")
async def menu_photos(callback: CallbackQuery, json_handler):
    years = await json_handler.get_years()
    # ВАЖНО: никакого <год> — иначе Telegram думает, что это HTML-тег
    text = (
        "Выбери год выезда:"
        if years
        else "Пока нет добавленных годов."
    )
    await callback.message.edit_text(text, reply_markup=years_kb(years))
    await callback.answer()

@router.callback_query(lambda c: c.data == "nav:years")
async def nav_years(callback: CallbackQuery, json_handler):
    years = await json_handler.get_years()
    await callback.message.edit_text("Выбери год выезда:", reply_markup=years_kb(years))
    await callback.answer()

@router.callback_query(lambda c: (c.data or "").startswith("year:"))
async def pick_year(callback: CallbackQuery):
    year = int(callback.data.split(":")[1])
    await callback.message.edit_text(f"Год {year}. Что показать?", reply_markup=year_actions_kb(year))
    await callback.answer()

@router.callback_query(lambda c: (c.data or "").startswith("yearphotos:"))
async def show_year_photos(callback: CallbackQuery, json_handler):
    year = int(callback.data.split(":")[1])
    photos = await json_handler.get_photos(year)

    if not photos:
        await callback.message.edit_text(
            f"За {year} фото пока нет.",
            reply_markup=year_actions_kb(year),
        )
        await callback.answer()
        return

    await callback.answer("Отправляю фото…")

    # Telegram media group: максимум 10
    sent_any = False
    for idx, pack in enumerate(_chunk(photos, 10)):
        media = []
        for j, fid in enumerate(pack):
            cap = f"🧊 Выезд {year}" if (idx == 0 and j == 0) else None
            media.append(InputMediaPhoto(media=fid, caption=cap))
        await callback.message.answer_media_group(media)
        sent_any = True

    if sent_any:
        await callback.message.answer(f"Год {year}: выбери действие ниже.", reply_markup=year_actions_kb(year))

@router.callback_query(lambda c: (c.data or "").startswith("yearinfo:"))
async def show_year_info(callback: CallbackQuery, json_handler):
    year = int(callback.data.split(":")[1])
    info = await json_handler.get_trip_info(year)
    # Экранируем info, чтобы админ мог писать любые символы
    await callback.message.edit_text(
        f"ℹ️ <b>{year}</b>\n\n{h(info)}",
        reply_markup=year_actions_kb(year),
    )
    await callback.answer()

@router.callback_query(lambda c: (c.data or "").startswith("yearlinks:"))
async def show_year_links(callback: CallbackQuery, json_handler):
    year = int(callback.data.split(":")[1])
    links = await json_handler.get_links(year)

    if not links:
        text = f"За {year} ссылок пока нет."
    else:
        # В ссылках HTML нужен, но title экранируем на всякий случай
        lines = [f"• <a href='{l['url']}'>{h(l.get('title', 'Ссылка'))}</a>" for l in links]
        text = f"🔗 <b>Ссылки {year}</b>\n\n" + "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=year_actions_kb(year))
    await callback.answer()
