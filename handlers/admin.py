from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.text_decorations import html_decoration as hd

router = Router()

class AddPhotoState(StatesGroup):
    waiting_photos = State()

def h(text: str) -> str:
    # чтобы даже в ответах (ParseMode.HTML) не ломалось
    return hd.quote(text or "")

def _is_admin(message: Message, admin_ids: set[int]) -> bool:
    return bool(message.from_user and (message.from_user.id in admin_ids))

@router.message(Command("add_photo"))
async def add_photo_cmd(message: Message, state: FSMContext, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return


    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.answer("Использование: /add_photo ГОД\nНапример: /add_photo 2024")

    year = int(parts[1].strip())
    await json_handler.upsert_trip(year)
    await state.update_data(year=year)
    await state.set_state(AddPhotoState.waiting_photos)

    await message.answer(
        f"Ок! Теперь отправь фото (можно пачкой). Я сохраню их для {year}.\n"
        f"Когда закончишь — напиши /done"
    )

@router.message(Command("done"))
async def done_cmd(message: Message, state: FSMContext):
    cur = await state.get_state()
    if cur == AddPhotoState.waiting_photos:
        await state.clear()
        await message.answer("Готово ✅")
    else:
        await message.answer("Нечего завершать 🙂")

@router.message(AddPhotoState.waiting_photos, F.photo)
async def add_photo_receive(message: Message, state: FSMContext, json_handler):
    data = await state.get_data()
    year = int(data["year"])
    file_id = message.photo[-1].file_id
    count = await json_handler.add_photo(year, file_id)
    await message.answer(f"Добавил фото к {year}. Всего фото: {count}")

@router.message(Command("set_info"))
async def set_info_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return


    # /set_info 2024 текст...
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await message.answer("Использование: /set_info ГОД ТЕКСТ\nНапример: /set_info 2024 Короткое описание")

    year = int(parts[1])
    text = parts[2].strip()
    await json_handler.set_trip_info(year, text)
    await message.answer(f"Инфо для {year} обновлено ✅")

@router.message(Command("add_link"))
async def add_link_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return
    

    # /add_link 2024 Название | https://...
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await message.answer(
            "Использование: /add_link ГОД Название | https://...\n"
            "Например: /add_link 2024 Группа ВК | https://vk.com/..."
        )

    year = int(parts[1])
    rest = parts[2]
    if "|" not in rest:
        return await message.answer("Формат: Название | https://...")

    title, url = [x.strip() for x in rest.split("|", maxsplit=1)]
    n = await json_handler.add_link(year, title, url)
    await message.answer(f"Ссылка добавлена к {year}. Всего ссылок: {n}")

@router.message(Command("set_history"))
async def set_history_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return


    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Использование: /set_history ТЕКСТ_ИСТОРИИ")

    await json_handler.set_history(parts[1].strip())
    await message.answer("История обновлена ✅")

@router.message(Command("add_common_link"))
async def add_common_link_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return


    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or "|" not in parts[1]:
        return await message.answer(
            "Использование: /add_common_link Название | https://...\n"
            "Например: /add_common_link Чат | https://t.me/..."
        )

    title, url = [x.strip() for x in parts[1].split("|", maxsplit=1)]
    n = await json_handler.add_common_link(title, url)
    await message.answer(f"Общая ссылка добавлена. Всего: {n}")

@router.message(Command("set_welcome_photo"), F.photo)
async def set_welcome_photo(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return  # тихо игнорируем неадминов

    # берём самое большое фото
    file_id = message.photo[-1].file_id
    await json_handler.set_welcome_photo(file_id)

    await message.answer("Приветственная фотография установлена ✅")


@router.message(Command("set_welcome_photo"))
async def set_welcome_photo_help(message: Message, admin_ids):
    if not _is_admin(message, admin_ids):
        return  # тихо игнорируем неадминов

    await message.answer(
        "Отправь команду <b>/set_welcome_photo</b> вместе с фотографией.\n"
        "Фото нужно прикрепить к сообщению."
    )