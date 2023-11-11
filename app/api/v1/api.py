from typing import Annotated, List, Union, Optional
from fastapi import APIRouter, Depends, Cookie, Response, UploadFile, HTTPException, Form, Body, File, Query
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from api.dependencies import get_prop_db, get_admin_db, authenticate, create_access_token, get_current_user, \
    create_refresh_token, change_pass
from core.dal import PropsManager, AdminManager
from core.models import PropsModel, Admin, FilterObj
from core.settings import settings
from utils.file_update import upload_file, remove_file, upload_project, discard_project, get_projects
from utils.query_format import serialize_query

age = settings.REFRESH_TOKEN_EXPIRE_MINUTES
app = APIRouter(prefix='/api')
admin = APIRouter(prefix='/api/admin')


def paginate_param(skip: int = 0, limit: Optional[int] = 100) -> dict:
    return {"skip": skip, "limit": limit}


Pagination = Annotated[dict, Depends(paginate_param)]


@admin.post('/token', description='get token for admin')
async def auth(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
               manager: AdminManager = Depends(get_admin_db)):
    user = await authenticate(username=form_data.username, password=form_data.password, manager=manager)
    access_token = create_access_token(data={'sub': user.get('username')})
    refresh_token = create_refresh_token(data={'sub': user.get('username')})
    response.set_cookie(key="refresh_token", value=refresh_token, path='/', httponly=True, max_age=60 * age)
    return {"access_token": access_token, "token_type": "bearer"}


# @admin.post('/reg', description='register admin')
# async def reg(admin_data: Admin, manager: AdminManager = Depends(get_admin_db)):
#     obj_id = await manager.add_admin(admin_data.hashed)
#     if not obj_id.get('_id'):
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Admin is already exists",
#         )
#     return obj_id

@admin.post('/logout', description="logout")
async def logout():
    response = Response()
    response.set_cookie(key="refresh_token", path='/', httponly=True, max_age=0)
    return response


@admin.put('/change_pass', description='change admin pass')
async def change_password(new_pass: dict, user: dict = Depends(get_current_user),
                          manager: AdminManager = Depends(get_admin_db)):
    await change_pass(user=user, new_pass=new_pass.get('pass'), manager=manager)


@admin.post('/refresh', description='refresh access token here')
async def refresh(refresh_token: Annotated[str | None, Cookie()]):
    user = await get_current_user(refresh_token)
    access_token = create_access_token(data={'sub': user.get('username')})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/ranges', description='fetch all values ranges')
async def fetch_ranges(manager: PropsManager = Depends(get_prop_db)):
    range_map = await manager.fetch_all_ranges()
    if range_map:
        return range_map
    else:
        return JSONResponse(status_code=404, content={})


@app.get('/props', description='fetch all props')
async def fetch_props(pagination: Pagination, filter_map: FilterObj = Depends(),
                      manager: PropsManager = Depends(get_prop_db)):
    serialized_filter_map = await serialize_query(filter_map, manager)
    return await manager.retrieve_all_props(pagination, serialized_filter_map)


@app.get('/props/{obj}', description='fetch one prop')
async def fetch_prop(obj: str, manager: PropsManager = Depends(get_prop_db)):
    return await manager.retrieve_prop(obj)


@admin.post('/props', description='create new prop in admin panel')
async def create_prop(props: PropsModel, manager: PropsManager = Depends(get_prop_db),
                      user: dict = Depends(get_current_user)):
    await manager.add_prop(props)
    return props.id


@admin.put('/props', description='update prop in admin panel')
async def patch_prop(prop_obj: PropsModel, manager: PropsManager = Depends(get_prop_db),
                     user: dict = Depends(get_current_user)):
    await manager.update_prop(prop_obj)


@admin.delete('/props/{obj}')
async def remove_prop(obj: str, manager: PropsManager = Depends(get_prop_db),
                      user: dict = Depends(get_current_user)):
    await manager.delete_prop(obj)
    remove_file(props_id=obj)


@admin.put('/static', description='upload files')
async def upload_img(props_id: Annotated[str, Form(...)], user: dict = Depends(get_current_user),
                     images: Annotated[List[UploadFile], Union[UploadFile, str]] = None,
                     plans: Annotated[List[UploadFile], Union[UploadFile, str]] = None,
                     videos: Annotated[List[UploadFile], Union[UploadFile, str]] = None,
                     manager: PropsManager = Depends(get_prop_db)):
    file_map = await upload_file(props_id=props_id, images=images, plans=plans, videos=videos)
    await manager.update_file(props_id=props_id, file_map=file_map)


@app.get('/projects', description='fetch all projects')
async def fetch_projects(response: list = Depends(get_projects)) -> list:
    return response


@admin.post('/projects', description='upload projects presentation')
async def upload_present(file: UploadFile, user: dict = Depends(get_current_user)):
    await upload_project(file)


@admin.delete('/projects/{prj}', description='remove project')
async def remove_project(status_code: int = Depends(discard_project), user: dict = Depends(get_current_user)):
    return Response(status_code=status_code)
