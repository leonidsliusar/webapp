import pytest
from pymongo.errors import DuplicateKeyError


async def test_retrieve(setup_and_teardown_db, add_prop_fix):
    assert await setup_and_teardown_db.retrieve_prop({'en.title': 'Test Title'}) == add_prop_fix


async def test_add_props(setup_and_teardown_db, stub_props):
    manager = setup_and_teardown_db
    await manager.add_prop(stub_props)
    result_map = stub_props.model_dump(by_alias=True)
    assert await manager.retrieve_prop({'en.title': 'Test Title'}) == result_map


async def test_delete_props(setup_and_teardown_db, add_prop_fix):
    manager = setup_and_teardown_db
    assert await manager.retrieve_prop({'en.title': 'Test Title'}) == add_prop_fix
    await manager.delete_prop({'en.title': 'Test Title'})
    assert not await manager.retrieve_prop({'en.title': 'Test Title'})


async def test_update_props(setup_and_teardown_db, add_prop_fix, stub_props):
    manager = setup_and_teardown_db
    result_map = add_prop_fix
    assert await manager.retrieve_prop({'en.title': 'Test Title'}) == result_map
    stub_props.en.title = 'New Test Title'
    await manager.update_prop(stub_props)
    result_map['en']['title'] = 'New Test Title'
    assert await manager.retrieve_prop({'en.title': 'New Test Title'}) == stub_props.model_dump(by_alias=True)


async def test_all_props(setup_and_teardown_db, add_props_fix):
    assert await setup_and_teardown_db.retrieve_all_props(filter_map={'property.region': 'kyrenia'}) == [add_props_fix[0]]


@pytest.mark.parametrize('expected_result', [
    {
        'type_en': ['type 1', 'type 2'],
        'type_de': ['type 1 DE'],
        'type_ru': [],
        'floor': [1, 10],
        'total_area': [30, 300],
        'rooms': [2, 5],
        'price': [50000, 100000]}
])
async def test_fetch_all_ranges(setup_and_teardown_db, add_props_fix, expected_result):
    assert await setup_and_teardown_db.fetch_all_ranges() == expected_result


async def test_insert_dict(setup_and_teardown_db, stub_props, stub_props_2):
    storage = setup_and_teardown_db
    await storage.insert_dict(stub_props)
    await storage.insert_dict(stub_props_2)
    assert await storage.retrieve_dict() == {
        'type_en': [stub_props.en.type, stub_props_2.en.type],
        'type_de': [item for item in {stub_props.de.type, stub_props_2.de.type}],
        'type_ru': [item for item in {
            stub_props.ru.type if stub_props.ru else None,
            stub_props_2.ru.type if stub_props_2.ru else None
        }]
    }


async def test_fetch_admin(setup_and_teardown_db_admin, add_admin_fix):
    assert await setup_and_teardown_db_admin.fetch_admin('test_username') == add_admin_fix


async def test_add_admin(setup_and_teardown_db_admin, stub_admin):
    await setup_and_teardown_db_admin.add_admin(stub_admin)
    admin_map = await setup_and_teardown_db_admin.fetch_admin(stub_admin.username)
    admin_map.pop('_id')
    assert admin_map == stub_admin.model_dump()


async def test_add_fail_admin(setup_and_teardown_db_admin, stub_admin):
    await setup_and_teardown_db_admin.add_admin(stub_admin)
    with pytest.raises(DuplicateKeyError):
        await setup_and_teardown_db_admin.add_admin(stub_admin)


async def test_update_pass(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    new_pass_admin = stub_admin
    new_pass_admin.password = 'new_pass'
    manager = setup_and_teardown_db_admin
    await manager.update_pass(new_pass_admin)
    db_admin_map = await manager.fetch_admin(stub_admin.username)
    db_admin_map.pop('_id')
    assert db_admin_map == new_pass_admin.model_dump()
