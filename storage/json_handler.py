from __future__ import annotations
from typing import Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

class JsonHandler:
    """
    Хранит "контент как JSON", но в MongoDB (чтобы на бесплатном хостинге ничего не терялось).
    Коллекции:
      - years: документы по годам
      - meta: история/общие ссылки
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.years = db["years"]
        self.meta = db["meta"]

    async def ensure_defaults(self) -> None:
        # Минимальные дефолты
        await self.meta.update_one(
            {"_id": "history"},
            {"$setOnInsert": {"text": "Пока тут пусто."}},
            upsert=True,
        )
        await self.meta.update_one(
            {"_id": "common_links"},
            {"$setOnInsert": {"links": []}},
            upsert=True,
        )

    # --------- Years / Trips ---------

    async def get_years(self) -> list[int]:
        cursor = self.years.find({}, {"_id": 1}).sort("_id", 1)
        years: list[int] = []
        async for doc in cursor:
            years.append(int(doc["_id"]))
        return years

    async def get_trip(self, year: int) -> Optional[dict[str, Any]]:
        return await self.years.find_one({"_id": int(year)})

    async def get_trip_info(self, year: int) -> str:
        doc = await self.get_trip(year)
        if not doc:
            return "Пока нет информации про этот год."
        return doc.get("info", "Пока нет информации про этот год.")

    async def get_photos(self, year: int) -> list[str]:
        doc = await self.get_trip(year)
        if not doc:
            return []
        return list(doc.get("photos", []))

    async def get_links(self, year: int) -> list[dict[str, str]]:
        doc = await self.get_trip(year)
        if not doc:
            return []
        return list(doc.get("links", []))

    async def upsert_trip(self, year: int, title: str | None = None) -> None:
        update = {"$setOnInsert": {"_id": int(year), "photos": [], "links": [], "info": ""}}
        if title:
            update.setdefault("$set", {})["title"] = title
        await self.years.update_one({"_id": int(year)}, update, upsert=True)

    async def add_photo(self, year: int, file_id: str) -> int:
        year = int(year)

        # 1) гарантируем, что документ существует (и нужные поля есть)
        await self.years.update_one(
            {"_id": year},
            {"$setOnInsert": {"photos": [], "links": [], "info": ""}},
            upsert=True,
        )

        # 2) добавляем фото
        await self.years.update_one(
            {"_id": year},
            {"$push": {"photos": file_id}},
        )

        # 3) возвращаем текущее количество
        doc = await self.years.find_one({"_id": year}, {"photos": 1})
        return len((doc or {}).get("photos", []))

    async def set_trip_info(self, year: int, info: str) -> None:
        await self.years.update_one(
            {"_id": int(year)},
            {"$setOnInsert": {"photos": [], "links": []}, "$set": {"info": info}},
            upsert=True,
        )

    async def add_link(self, year: int, title: str, url: str) -> int:
        year = int(year)

        await self.years.update_one(
            {"_id": year},
            {"$setOnInsert": {"photos": [], "links": [], "info": ""}},
            upsert=True,
        )

        await self.years.update_one(
            {"_id": year},
            {"$push": {"links": {"title": title, "url": url}}},
        )

        doc = await self.years.find_one({"_id": year}, {"links": 1})
        return len((doc or {}).get("links", []))


    # --------- Meta ---------

    async def get_history(self) -> str:
        doc = await self.meta.find_one({"_id": "history"})
        return (doc or {}).get("text", "")

    async def set_history(self, text: str) -> None:
        await self.meta.update_one({"_id": "history"}, {"$set": {"text": text}}, upsert=True)

    async def get_common_links(self) -> list[dict[str, str]]:
        doc = await self.meta.find_one({"_id": "common_links"})
        return list((doc or {}).get("links", []))

    async def add_common_link(self, title: str, url: str) -> int:
        doc = await self.meta.find_one_and_update(
            {"_id": "common_links"},
            {"$setOnInsert": {"links": []}, "$push": {"links": {"title": title, "url": url}}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return len(doc.get("links", [])) if doc else 0
    
    async def set_welcome_photo(self, file_id: str) -> None:
        await self.meta.update_one(
            {"_id": "welcome_photo"},
            {"$set": {"file_id": file_id}},
            upsert=True,
        )

    async def get_welcome_photo(self) -> str | None:
        doc = await self.meta.find_one({"_id": "welcome_photo"})
        return (doc or {}).get("file_id")
    
    async def get_db_stats(self) -> dict:
        # MongoDB dbStats: размеры в байтах
        return await self.db.command("dbStats")