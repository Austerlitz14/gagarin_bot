import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import load_settings
from storage.mongo import get_db
from storage.json_handler import JsonHandler

from handlers.start import router as start_router
from handlers.photos import router as photos_router
from handlers.history import router as history_router
from handlers.links import router as links_router
from handlers.admin import router as admin_router


def build_dispatcher(settings, json_handler: JsonHandler) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Простая DI (dependency injection): кладём зависимости в workflow_data,
    # и aiogram сам прокинет их в хэндлеры по имени аргумента.
    dp.workflow_data.update({
        "json_handler": json_handler,
        "admin_ids": settings.admin_ids,
    })

    dp.include_router(start_router)
    dp.include_router(photos_router)
    dp.include_router(history_router)
    dp.include_router(links_router)
    dp.include_router(admin_router)
    return dp


async def on_startup(dispatcher: Dispatcher, bot: Bot, settings, json_handler: JsonHandler) -> None:
    await json_handler.ensure_defaults()
    webhook_url = f"{settings.base_url}{settings.webhook_path}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.webhook_secret,
        drop_pending_updates=True,
    )
    logging.info("Webhook set to %s", webhook_url)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=False)
    logging.info("Webhook deleted")


async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    settings = load_settings()

    # Render/другие PaaS обычно дают PORT в env
    port = int((__import__("os").getenv("PORT") or "8080"))
    host = "0.0.0.0"

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async def make_app() -> web.Application:
        db = await get_db(settings.mongo_uri, settings.mongo_db)
        json_handler = JsonHandler(db)
        dp = build_dispatcher(settings, json_handler)

        dp.startup.register(lambda *args, **kwargs: on_startup(dp, bot, settings, json_handler))
        dp.shutdown.register(lambda *args, **kwargs: on_shutdown(bot))

        app = web.Application()

        # /health — удобно для UptimeRobot (не обязателен)
        app.router.add_get("/health", health)

        # Webhook handler
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.webhook_secret,
        )
        webhook_handler.register(app, path=settings.webhook_path)

        setup_application(app, dp, bot=bot)
        return app

    app = web.Application()

    async def init_app():
        real_app = await make_app()
        return real_app

    web.run_app(init_app(), host=host, port=port)


if __name__ == "__main__":
    main()
