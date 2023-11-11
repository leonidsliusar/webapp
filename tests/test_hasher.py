import pytest

from app.utils.hasher import hash_pass, check_hash


@pytest.mark.parametrize('password', ['123456', '3fsf3', 'Ddf33#@#FDSF#'])
def test_hash(password: str):
    hashed = hash_pass(password)
    assert hashed != password
    assert check_hash(password, hashed)
