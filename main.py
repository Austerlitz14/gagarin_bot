import os
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# --- your imports ---
from config import load_settings
from storage.mongo import get_db
from storage.json_handler import JsonHandler

from handlers.start import router as start_router
from handlers.photos import router as photos_router
from handlers.history import router as history_router
from handlers.links import router as links_router
from handlers.admin import router as admin_router


async def root(request: web.Request) -> web.Response:
    return web.Response(text="ok")

async def health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


def build_dispatcher(settings, json_handler: JsonHandler) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Dependency injection по именам аргументов в хэндлерах
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


async def main() -> web.Application:
    logging.basicConfig(level=logging.INFO)

    settings = load_settings()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    db = await get_db(settings.mongo_uri, settings.mongo_db)
    json_handler = JsonHandler(db)
    await json_handler.ensure_defaults()

    dp = build_dispatcher(settings, json_handler)

    # --- aiohttp app ---
    app = web.Application()
    app.router.add_get("/", root)
    app.router.add_get("/health", health)

    # Webhook endpoint path
    webhook_path = settings.webhook_path or "/webhook"
    if not webhook_path.startswith("/"):
        webhook_path = "/" + webhook_path

    # Register webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    ).register(app, path=webhook_path)

    setup_application(app, dp, bot=bot)

    # --- set webhook on startup ---
    async def on_startup(app_: web.Application) -> None:
        webhook_url = f"{settings.base_url}{webhook_path}"
        logging.info("Setting webhook: %s", webhook_url)

        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
        )

        logging.info("Webhook set OK")

# async def on_cleanup(app_: web.Application) -> None:
#     logging.info("Deleting webhook...")
#     await bot.delete_webhook(drop_pending_updates=False)
#     logging.info("Webhook deleted")

    app.on_startup.append(on_startup)
 #   app.on_cleanup.append(on_cleanup)

    return app


if __name__ == "__main__":
    # Render sets PORT
    port = int(os.getenv("PORT", "10000"))
    web.run_app(main(), host="0.0.0.0", port=port)
