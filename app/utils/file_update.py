import os
import re
import shutil

from fastapi import UploadFile
from pdf2image import convert_from_bytes


async def upload_file(props_id: str, images: list, plans: list, videos: list) -> dict:
    obj_path = f'static/{props_id}'
    if os.path.exists(obj_path):
        shutil.rmtree(obj_path)
    os.makedirs(f'{obj_path}/img')
    os.makedirs(f'{obj_path}/plan')
    os.makedirs(f'{obj_path}/video')
    file_map = {'img_link': [], 'plan_link': [], 'video_link': []}
    if images:
        for i in range(len(images)):
            img = images[i]
            img_path = f'{obj_path}/img/{i}_{img.filename}'
            file_map.get('img_link').append(img_path)
            with open(img_path, 'wb') as file:
                file.write(await img.read())
    if plans:
        for j in range(len(plans)):
            plan = plans[j]
            plan_path = f'{obj_path}/plan/{j}_{plan.filename}'
            file_map.get('plan_link').append(plan_path)
            with open(plan_path, 'wb') as file:
                file.write(await plan.read())
    if videos:
        for k in range(len(videos)):
            video = videos[k]
            video_path = f'{obj_path}/video/{k}_{video.filename}'
            file_map.get('video_link').append(video_path)
            with open(video_path, 'wb') as file:
                file.write(await video.read())
    return file_map


def remove_file(props_id: str) -> None:
    obj_path = f'static/{props_id}'
    if os.path.exists(obj_path):
        shutil.rmtree(obj_path)


def get_projects() -> list:
    folder_path = 'static/projects'
    files = os.listdir(folder_path)
    return files


async def upload_project(file: UploadFile) -> None:
    obj_path = 'static/projects'
    if not os.path.exists(obj_path):
        os.makedirs(f'{obj_path}')
    with open(f'{obj_path}/{file.filename}', 'wb') as doc:
        file_data = await file.read()
        doc.write(file_data)
        title_image = convert_from_bytes(file_data)
        if title_image:
            title_image[0].save(f'{obj_path}/{file.filename}.jpg', 'JPEG')


def discard_project(prj: str) -> int:
    obj_path = f'static/projects/{prj}'
    obj_path_pdf = re.sub(r"\.jpg$", "", obj_path)
    if os.path.exists(obj_path):
        os.remove(obj_path)
        os.remove(obj_path_pdf)
        return 200
    else:
        return 404
