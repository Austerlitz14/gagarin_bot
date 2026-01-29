from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

async def get_db(mongo_uri: str, db_name: str) -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(mongo_uri)
    return client[db_name]
