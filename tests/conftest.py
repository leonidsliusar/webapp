import os
from datetime import date, datetime
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.dal import PropsManager, AdminManager
from app.core.models import ObjProperty, PropsModel, LangProperty, Admin


@pytest.fixture()
def setup_and_teardown_db_admin():
    client = AsyncIOMotorClient('localhost', 27018)
    db = client.db_test
    collection = db.test
    manager = AdminManager(collection)
    os.system('docker compose -f tests/docker-compose-test.yml up -d')
    yield manager
    os.system('docker compose -f tests/docker-compose-test.yml down -v')


@pytest.fixture()
async def add_admin_fix(stub_admin):
    client = AsyncIOMotorClient('localhost', 27018)
    db = client.db_test
    collection = db.test
    document = stub_admin.hashed.model_dump()
    await collection.insert_one(document)
    yield document


@pytest.fixture()
def stub_admin() -> Admin:
    return Admin(username='test_username', password='test_pass')


@pytest.fixture()
def setup_and_teardown_db():
    client = AsyncIOMotorClient('localhost', 27018)
    db = client.db_props
    collection = db.props
    db_dict_map = db.dict_map
    manager = PropsManager(collection, db_dict_map)
    os.system('docker compose -f tests/docker-compose-test.yml up -d')
    yield manager
    os.system('docker compose -f tests/docker-compose-test.yml down -v')


@pytest.fixture()
async def add_prop_fix(stub_props):
    client = AsyncIOMotorClient('localhost', 27018)
    db = client.db_props
    collection = db.props
    document = stub_props.model_dump(by_alias=True)
    await collection.insert_one(document)
    yield document


@pytest.fixture()
async def add_props_fix(stub_props, stub_props_2):
    client = AsyncIOMotorClient('localhost', 27018)
    db = client.db_props
    collection = db.props
    stub_props.property.serialize_completion()
    stub_props_2.property.serialize_completion()
    document = stub_props.model_dump(by_alias=True)
    document2 = stub_props_2.model_dump(by_alias=True)
    await collection.insert_many((document, document2))
    yield [document, document2]


@pytest.fixture()
def stub_props() -> PropsModel:
    lang_property_map = {
        'title': 'Test Title',
        'description': 'Test Description',
    }
    lang_property_map_de = {
        'title': 'Test Title',
        'description': 'Test Description',
    }
    obj_property_map = {
        'price': 100000,
        'type': 'apartment',
        'region': 'kyrenia',
        'photos': ['img_1.jpg', 'img_2.jpg'],
        'floor': 10,
        'closed_area': 25,
        'total_area': 30,
        'rooms': 2,
        'bedrooms': 1,
        'pool': 'public',
        'completion': date(24, 12, 12)
    }
    lang_property = LangProperty(**lang_property_map)
    obj_property = ObjProperty(**obj_property_map)
    data_map = {
        '_id': 1,
        'property': obj_property,
        'en': lang_property,
        'de': lang_property_map_de,
        'created_at': datetime(70, 1, 1, 0, 0),
        'upd_at': datetime(70, 1, 1, 0, 0)
    }
    obj_props = PropsModel(**data_map)
    return obj_props


@pytest.fixture()
def stub_props_2() -> PropsModel:
    lang_property_map = {
        'title': 'Test Title 2',
        'description': 'Test Description 2',
    }
    lang_property_map_de = {
        'title': 'Test Title 2',
        'description': 'Test Description 2',
    }
    obj_property_map = {
        'region': 'iskele',
        'type': 'villa',
        'price': 50000,
        'photos': ['img_3.jpg', 'img_4.jpg'],
        'floor': 1,
        'closed_area': 250,
        'total_area': 300,
        'rooms': 5,
        'bedrooms': 1,
        'pool': 'private',
        'completion': date(24, 12, 12)
    }
    lang_property = LangProperty(**lang_property_map)
    obj_property = ObjProperty(**obj_property_map)
    obj_props = PropsModel(
        _id=2,
        property=obj_property,
        en=lang_property,
        de=lang_property_map_de,
        created_at=datetime(70, 1, 1, 0, 0),
        upd_at=datetime(70, 1, 1, 0, 0)
    )
    return obj_props
