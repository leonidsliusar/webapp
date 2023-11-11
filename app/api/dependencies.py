from datetime import timedelta, datetime
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer
from core.models import Admin
from core.settings import settings
from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from starlette import status
from core.dal import PropsManager, AdminManager
from utils.hasher import check_hash

props_manager = PropsManager()
admin_manager = AdminManager()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_prop_db() -> PropsManager:
    return props_manager


async def get_admin_db() -> AdminManager:
    return admin_manager


async def get_db_user(username: str, manager: AdminManager) -> Optional[dict]:
    admin_db = await manager.fetch_admin(username)
    return admin_db


async def authenticate(username: str, password: str, manager: AdminManager) -> dict:
    admin_db = await get_db_user(username, manager)
    if not admin_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    hashed_pass = admin_db.get('password')
    if not check_hash(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin_db


def create_access_token(data: dict, expires: float = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    manager = await get_admin_db()
    user = await get_db_user(username=username, manager=manager)
    if user is None:
        raise credentials_exception
    return user


async def change_pass(user: dict, new_pass: str, manager: AdminManager):
    username = user.get('username')
    old_hashed_pass = user.get('password')
    if check_hash(new_pass, old_hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An old and a new password are equal",
        )
    admin = Admin(username=username, password=new_pass).hashed
    await manager.update_pass(admin)
