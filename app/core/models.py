import json
from datetime import datetime, date
from enum import Enum
from typing import Optional, Union
from uuid import uuid4
from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from utils.hasher import hash_pass


class TitleType(str, Enum):
    tur = 'tur'
    eqv = 'eqv'
    al = 'al'


class Region(str, Enum):
    kyrenia = 'kyrenia'
    famagusta = 'famagusta'
    iskele = 'iskele'
    nicosia = 'nicosia'
    guzelyurt = 'guzelyurt'


class LangProperty(BaseModel):
    title: str
    description: str


class Pool(str, Enum):
    none = '-'
    soc = 'public'
    prv = 'private'


class ObjType(str, Enum):
    apartment = 'apartment'
    penthouse = 'penthouse'
    villa = 'villa'
    bungalow = 'bungalow'
    land = 'land'


class SaleType(str, Enum):
    rent = 'rent'
    new = 'new'
    resale = 'resale'


class ObjProperty(BaseModel):
    type: ObjType
    region: Region
    price: Union[int, float]
    total_area: Union[float, int]
    floor: Optional[int] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    closed_area: Optional[Union[float, int]] = None
    sale_type: Optional[SaleType] = None
    pool: Optional[Pool] = None
    completion: Optional[date | datetime | str] = None
    title_type: Optional[TitleType] = None
    terrace: Optional[list[Optional[int]]] = None
    balcony: Optional[list[Optional[int]]] = None
    map_url: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.rooms:
            self.bedrooms = self.rooms - 1

    @field_validator('completion')
    @classmethod
    def validate_completion_format(cls, v: str | datetime | date):
        if isinstance(v, str):
            try:
                date_object = datetime.strptime(v + '-01', '%Y-%m-%d')
                formatted_date = date_object.strftime('%Y-%m-%d')
                date_result = datetime.strptime(formatted_date, '%Y-%m-%d').date()
                return date_result
            except ValueError:
                raise ValueError('Invalid format. Format should be YYYY-MM')
        else:
            return v

    def serialize_completion(self):
        if self.completion:
            self.completion = datetime(self.completion.year, self.completion.month, day=1, hour=0, minute=0, second=0)


class PropsModel(BaseModel):
    id: str = Field(alias='_id')
    property: ObjProperty
    en: LangProperty
    de: LangProperty
    ru: LangProperty
    fr: LangProperty
    tr: LangProperty
    img_link: list[Optional[str]] = []
    plan_link: list[Optional[str]] = []
    video_link: list[Optional[str]] = []
    created_at: datetime = datetime.today().replace(second=0, microsecond=0)
    upd_at: datetime = datetime.today().replace(second=0, microsecond=0)

    def serialize_for_task(self) -> str:
        obj_map = {
            'id': self.id,
            'title': self.de.title,
            'description': self.de.description,
            'img_link': self.img_link,
            'region': self.property.region,
            'price': self.property.price
        }
        return json.dumps(obj_map)


class Admin(BaseModel):
    username: str
    password: str

    @property
    def hashed(self):
        hashed_pass = hash_pass(password=self.password)
        return HashedAdmin(username=self.username, password=hashed_pass)


class HashedAdmin(BaseModel):
    username: str
    password: str


class FilterObj(BaseModel):
    id: Optional[str] = Field(alias='_id', default=None)
    title: Optional[str] = None
    type: Optional[str] = None
    region: Optional[str] = None
    rooms: list[int] = Field(Query([]))
    price: list[int] = Field(Query([]))
    floor: list[int] = Field(Query([]))
    closed_area: list[int] = Field(Query([]))
    total_area: list[int] = Field(Query([]))

    @property
    def serialize(self) -> dict:
        filter_map = {}
        obj_attrs = vars(self)
        for key in obj_attrs:
            if value := obj_attrs.get(key):
                if key == 'title':
                    filter_map.update(self._serialize_title(value))
                elif key in ('region', 'type'):
                    filter_map.update(self._serialize_param(key, value))
                else:
                    filter_map.update(self._serialize_array_param(key, value))
        return filter_map

    @staticmethod
    def _serialize_title(value: str) -> dict:
        regex = {"$regex": f".*{value}.*", "$options": "i"}
        val_filter = {
            "$or": [
                {'en.title': regex},
                {'de.title': regex},
                {'ru.title': regex},
            ]
        }
        return val_filter

    @staticmethod
    def _serialize_param(key: str, value: str) -> dict:
        val_filter = {f"property.{key}": value}
        return val_filter

    def _serialize_array_param(self, key: str, value: list) -> dict:
        val_filter = {f"property.{key}": {"$gte": value[0], "$lte": value[1]}}
        return val_filter
