from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from core.settings import settings

host: str = settings.MONGO_HOST
port: int = settings.MONGO_PORT
user: str = settings.MONGO_USER
password: str = settings.MONGO_PASS
client: AsyncIOMotorClient = AsyncIOMotorClient(host=host, port=port, username=user, password=password)
db: AsyncIOMotorDatabase = client.db_props
collection: AsyncIOMotorCollection = db.props
admin_collection: AsyncIOMotorCollection = db.admin
dictionary_collection: AsyncIOMotorCollection = db.dict_map
