from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()

class AddPhotoState(StatesGroup):
    waiting_photos = State()

def _is_admin(message: Message, admin_ids: set[int]) -> bool:
    return message.from_user and (message.from_user.id in admin_ids)

@router.message(Command("add_photo"))
async def add_photo_cmd(message: Message, state: FSMContext, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return await message.answer("⛔️ Только для админов.")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        return await message.answer("Использование: /add_photo <год>\nНапример: /add_photo 2024")
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
    # берем самое большое фото
    file_id = message.photo[-1].file_id
    count = await json_handler.add_photo(year, file_id)
    await message.answer(f"Добавил фото к {year}. Всего фото: {count}")

@router.message(Command("set_info"))
async def set_info_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return await message.answer("⛔️ Только для админов.")
    # /set_info 2024 текст...
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await message.answer("Использование: /set_info <год> <текст>")
    year = int(parts[1])
    text = parts[2].strip()
    await json_handler.set_trip_info(year, text)
    await message.answer(f"Инфо для {year} обновлено ✅")

@router.message(Command("add_link"))
async def add_link_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return await message.answer("⛔️ Только для админов.")
    # /add_link 2024 Название | https://...
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        return await message.answer("Использование: /add_link <год> Название | https://...")
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
        return await message.answer("⛔️ Только для админов.")
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        return await message.answer("Использование: /set_history <текст истории>")
    await json_handler.set_history(text[1].strip())
    await message.answer("История обновлена ✅")

@router.message(Command("add_common_link"))
async def add_common_link_cmd(message: Message, admin_ids, json_handler):
    if not _is_admin(message, admin_ids):
        return await message.answer("⛔️ Только для админов.")
    rest = message.text.split(maxsplit=1)
    if len(rest) < 2 or "|" not in rest[1]:
        return await message.answer("Использование: /add_common_link Название | https://...")
    title, url = [x.strip() for x in rest[1].split("|", maxsplit=1)]
    n = await json_handler.add_common_link(title, url)
    await message.answer(f"Общая ссылка добавлена. Всего: {n}")
