import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing env var: {name}")
    return value

def _parse_admin_ids(raw: str) -> set[int]:
    raw = (raw or "").strip()
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}

@dataclass(frozen=True)
class Settings:
    bot_token: str
    base_url: str
    webhook_path: str
    webhook_secret: str
    mongo_uri: str
    mongo_db: str
    admin_ids: set[int]

def load_settings() -> Settings:
    return Settings(
        bot_token=_require("BOT_TOKEN"),
        base_url=_require("BASE_URL").rstrip("/"),
        webhook_path=os.getenv("WEBHOOK_PATH", "/webhook").strip() or "/webhook",
        webhook_secret=_require("WEBHOOK_SECRET"),
        mongo_uri=_require("MONGO_URI"),
        mongo_db=os.getenv("MONGO_DB", "gagarin_bot").strip() or "gagarin_bot",
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
    )
