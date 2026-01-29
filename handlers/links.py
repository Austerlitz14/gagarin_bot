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
        text = "Пока нет общих ссылок."
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
        "✨<b>Наш Гимн</b>✨\n\n"
        "Кинуть сумку на плечо,\n"
        "Сесть в автобус и уснуть.\n"
        "Глаза хочу открыть я там,\n"
        "Где сердечко колет грудь.\n"
        "\n"
        "Нарисую на стекле\n"
        "Белым мелом февраля,\n"
        "Как классно думать, что я тут\n"
        "Ведь десант - моя семья.\n"
        "\n"
        "Не запустим мы ракеты,\n"
        "Не взлетим мы в небеса.\n"
        "С нами <i>Юность</i> всей планеты,\n"
        "И <i>Искра</i> горит в глазах.\n"
        "Мы <i>Свободные,</i> как <i>Джанго</i>,\n"
        "Просто <i>Пламенем</i> маня,\n"
        "Мы едем вместе в поселенье,\n"
        "Чтоб опять зажечь сердца. x2\n"
        "\n"
        "Снежный ястреб, белый друг\n"
        "Соберёт нас в дружный круг.\n"
        "<i>Орионова</i> звезда, где рука в руке всегда;\n"
        "Пускай дорога не легка,\n"
        "И забросит нас туда,\n"
        "Где дым из печки и уют\n"
        "Таких, как мы, всегда там ждут.\n"
        "Не свернём с её пути\n"
        "---------------\n"
        "<b>Князь Гагарин</b> - это мы!\n"
        "\n"
        "В зал запустим все ракеты,\n"
        "На одной взлетим туда,\n"
        "Где небо яркое в <i>Созвездьях</i>\n,"
        "Где горит одна звезда.\n"
        "\n"
        "Руку помощи протянем,\n"
        "Всем кому она нужна.\n"
        "Такие вот у нас ребята!\n,"
        "Такая снежная зима-а-а.\n"
        "\n"
        "Такая снежная зима-а-а.\n"
        "Такая нежная зима-а-а.\n",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()
