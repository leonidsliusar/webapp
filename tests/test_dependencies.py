import asyncio
import pytest
from fastapi import HTTPException
from app.api.dependencies import get_db_user, change_pass, create_access_token, get_current_user, create_refresh_token, \
    authenticate
from app.utils.hasher import check_hash, hash_pass


async def tests_get_db_user(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    db_user_map = await get_db_user(username=stub_admin.username, manager=setup_and_teardown_db_admin)
    assert db_user_map == add_admin_fix


async def tests_change_pass(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    manager = setup_and_teardown_db_admin
    await change_pass(user=add_admin_fix, new_pass='new_pass', manager=manager)
    user_map = await get_db_user(username=stub_admin.username, manager=manager)
    new_pass = user_map.get('password')
    assert stub_admin.password != new_pass


async def tests_fail_change_pass(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    manager = setup_and_teardown_db_admin
    with pytest.raises(HTTPException) as e:
        await change_pass(user=add_admin_fix, new_pass=stub_admin.password, manager=manager)
    assert e.value.detail == 'An old and a new password are equal'


@pytest.mark.parametrize('data', [{'sub': 'username'}])
def tests_create_token(data: dict):
    assert create_access_token(data)
    assert create_refresh_token(data)


async def tests_get_current_user(setup_and_teardown_db_admin, add_admin_fix):
    token = create_access_token({'sub': 'test_username'})
    user_map = await get_current_user(token, setup_and_teardown_db_admin)
    user_map.pop('_id')
    assert user_map.get('username') == 'test_username'
    assert check_hash('test_pass', user_map.get('password'))


async def tests_fail_get_current_user(setup_and_teardown_db_admin, add_admin_fix):
    manager = setup_and_teardown_db_admin
    token = create_access_token({'sub': 'test_username'}, 0.0001)
    await asyncio.sleep(1)
    with pytest.raises(HTTPException) as e:
        assert await get_current_user(token, manager) == ''
    assert e.value.detail == 'Could not validate credentials'


async def tests_authenticate(setup_and_teardown_db_admin, add_admin_fix, stub_admin):
    user_map = await authenticate(stub_admin.username, stub_admin.password, setup_and_teardown_db_admin)
    user_map.pop('_id')
    hashed_pass = user_map.pop('password')
    user_map_result = {'username': stub_admin.username}
    assert user_map == user_map_result
    assert check_hash(password=stub_admin.password, hashed=hashed_pass)


@pytest.mark.parametrize('uname, pwr, expected_result', [
    ('username', 'test_pass', 'Invalid username'),
    ('test_username', 'pass', 'Invalid password')
])
async def tests_fail_authenticate(setup_and_teardown_db_admin, add_admin_fix, stub_admin, uname, pwr, expected_result):
    with pytest.raises(HTTPException) as e:
        await authenticate(uname, pwr, setup_and_teardown_db_admin)
    assert e.value.detail == expected_result
