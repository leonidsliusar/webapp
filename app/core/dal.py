from typing import Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from core.models import PropsModel, Admin
from core.mongo_config import collection, admin_collection, dictionary_collection


class PropsManager:

    def __init__(self, db_collection: AsyncIOMotorCollection = collection,
                 db_dict_map: AsyncIOMotorCollection = dictionary_collection):
        self._collection: AsyncIOMotorCollection = db_collection
        self._dict_collection: AsyncIOMotorCollection = db_dict_map

    async def retrieve_all_props(self, pagination: Optional[dict] = None, filter_map: Optional[dict] = None) -> dict[str, int|list]:
        filter_map = filter_map if filter_map else {}
        qnt = await self._collection.count_documents(filter_map)
        cursor = self._collection.find(filter_map)
        if pagination:
            if 'limit' in pagination:
                limit = pagination.get('limit')
                cursor.limit(limit)
            if 'skip' in pagination:
                skip = pagination.get('skip')
                cursor.skip(skip)
        documents = []
        async for document in cursor:
            documents.append(document)
        return {'qnt': qnt, 'docs': documents}

    async def fetch_all_ranges(self) -> dict:
        cursor = self._collection.aggregate([
            {
                '$group': {
                    '_id': None,
                    'floorMin': {'$min': '$property.floor'},
                    'floorMax': {'$max': '$property.floor'},
                    'areaLivingMin': {'$min': '$property.closed_area'},
                    'areaLivingMax': {'$max': '$property.closed_area'},
                    'areaMin': {'$min': '$property.total_area'},
                    'areaMax': {'$max': '$property.total_area'},
                    'roomsMin': {'$min': '$property.rooms'},
                    'roomsMax': {'$max': '$property.rooms'},
                    'priceMin': {'$min': '$property.price'},
                    'priceMax': {'$max': '$property.price'},
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'floor': ['$floorMin', '$floorMax'],
                    'total_area': ['$areaMin', '$areaMax'],
                    'closed_area': ['$areaLivingMin', '$areaLivingMax'],
                    'rooms': ['$roomsMin', '$roomsMax'],
                    'price': ['$priceMin', '$priceMax'],
                }
            }
        ])
        try:
            result = await cursor.next()
        except StopAsyncIteration:
            result = {}
        return result

    async def retrieve_prop(self, obj: str) -> dict:
        document = await self._collection.find_one(filter={'_id': obj})
        return document

    async def add_prop(self, props: PropsModel) -> dict:
        props.property.serialize_completion()
        result = await self._collection.insert_one(props.model_dump(by_alias=True, exclude_none=True))
        return {'_id': result.inserted_id}

    async def retrieve_dict(self) -> dict:
        return await self._dict_collection.find_one({'_id': 'type_dict'}, {'_id': 0})

    async def delete_prop(self, obj: str) -> None:
        await self._collection.delete_one(filter={'_id': obj})

    async def update_prop(self, props: PropsModel) -> None:
        props.property.serialize_completion()
        await self._collection.update_one(filter={'_id': props.id}, update={'$set': props.model_dump(by_alias=True, exclude_none=True)})

    async def update_file(self, props_id: str, file_map: dict) -> None:
        await self._collection.update_one(filter={'_id': props_id}, update={'$set': file_map})


class AdminManager:

    def __init__(self, db_collection: AsyncIOMotorCollection = admin_collection):
        self._collection: AsyncIOMotorCollection = db_collection

    async def add_admin(self, data: Admin) -> dict:
        await self._collection.create_index('username', unique=True)
        try:
            result = await self._collection.insert_one(data.model_dump())
            return {'_id': result.inserted_id.__str__()}
        except DuplicateKeyError:
            return {'_id': None}

    async def fetch_admin(self, username: str) -> dict:
        return await self._collection.find_one({'username': username})

    async def update_pass(self, data: Admin) -> None:
        await self._collection.update_one({'username': data.username}, {'$set': {'password': data.password}})
