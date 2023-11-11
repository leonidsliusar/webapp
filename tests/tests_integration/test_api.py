import pytest
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException
from app.api.v1.api import fetch_props, fetch_prop, create_prop, patch_prop, remove_prop, reg, auth
from app.core.models import PropsModel, Admin
from app.utils.hasher import check_hash


async def test_fetch_props(setup_and_teardown_db, add_props_fix):
    assert await fetch_props(manager=setup_and_teardown_db) == add_props_fix


async def test_fetch_prop(setup_and_teardown_db, add_props_fix):
    assert await fetch_prop(props_param={'_id': 1}, manager=setup_and_teardown_db) == add_props_fix[0]


@pytest.mark.parametrize('username, password', [('test_user', 'test_pass')])
async def test_reg(setup_and_teardown_db_admin, username, password):
    manager = setup_and_teardown_db_admin
    admin_data = Admin(username=username, password=password)
    result = await reg(admin_data, manager)
    result.pop('_id')
    assert check_hash(password, result.get('password'))


async def test_auth(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    manager = setup_and_teardown_db_admin
    user = OAuth2PasswordRequestForm(username=stub_admin.username, password=stub_admin.password)
    token = await auth(user, manager)
    assert 'access_token' in token


@pytest.mark.parametrize('username, password, result', [
    ('foo', 'test_pass', 'Invalid username'),
    ('test_username', 'foo', 'Invalid password')
])
async def test_fail_auth(setup_and_teardown_db_admin, add_admin_fix, stub_admin, username, password, result):
    manager = setup_and_teardown_db_admin
    user = OAuth2PasswordRequestForm(username=username, password=password)
    with pytest.raises(HTTPException) as e:
        await auth(user, manager)
    assert str(e.value.detail) == result


async def test_admin_fetch_props(setup_and_teardown_db, add_props_fix):
    assert await fetch_props(manager=setup_and_teardown_db) == add_props_fix


async def test_admin_fetch_prop(setup_and_teardown_db, add_props_fix):
    assert await fetch_prop(props_param={'_id': 1}, manager=setup_and_teardown_db) == add_props_fix[0]


async def test_create_prop(setup_and_teardown_db, stub_props):
    manager = setup_and_teardown_db
    assert await create_prop(prop_obj=stub_props, manager=manager) == {'_id': 1}
    assert await fetch_prop(props_param={'_id': 1}, manager=manager) == stub_props.model_dump(by_alias=True)


async def test_patch_prop(setup_and_teardown_db, add_prop_fix, stub_props):
    manager = setup_and_teardown_db
    obj_map = add_prop_fix
    obj_map['en'].update({'title': 'New Test Title'})
    new_obj = PropsModel(**obj_map)
    await patch_prop(prop_obj=new_obj, manager=manager)
    assert await fetch_prop(props_param={'_id': 1}, manager=manager) == obj_map


async def test_remove_prop(setup_and_teardown_db, add_prop_fix):
    manager = setup_and_teardown_db
    assert await fetch_prop(props_param={'_id': 1}, manager=manager)
    await remove_prop({'en.title': 'Test Title'}, manager=manager)
    assert not await fetch_prop(props_param={'_id': 1}, manager=manager)
