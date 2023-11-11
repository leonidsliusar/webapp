from datetime import date, datetime

import pytest

from app.core.models import LangProperty, ObjProperty, PropsModel, Admin, HashedAdmin
from app.utils.hasher import hash_pass


def test_props_serialize():
    lang_property_map = {
        'title': 'Test Title',
        'description': 'Test Description',
        'type': 'flat'
    }
    obj_property_map = {
        'price': 100000,
        'photos': ['img_1.jpg', 'img_2.jpg'],
        'map_url': 'https://google.com',
        'floor': 1,
        'closed_area': 25,
        'total_area': 30,
        'rooms': 2,
        'bedrooms': 1,
        'pool': 1,
        'completion': datetime(24, 12, 12, 0, 0)
    }
    lang_property = LangProperty(**lang_property_map)
    obj_property = ObjProperty(**obj_property_map)
    obj_props = PropsModel(
        property=obj_property,
        en=lang_property,
        created_at=datetime(70, 1, 1, 0, 0),
        upd_at=datetime(70, 1, 1, 0, 0)
    )
    map_props = obj_props.model_dump()
    map_props.pop('id')
    assert map_props == {
                        'property': {'balcony': None,
                                     'bedrooms': 1,
                                     'closed_area': 25.0,
                                     'completion': datetime(24, 12, 12, 0, 0),
                                     'floor': 1,
                                     'map_url': 'https://google.com',
                                     'photos': ['img_1.jpg', 'img_2.jpg'],
                                     'pool': 1,
                                     'price': 100000,
                                     'rooms': 2,
                                     'terrace': None,
                                     'total_area': 30.0},
                        'en': {'description': 'Test Description',
                               'title': 'Test Title',
                               'type': 'flat'},
                        'de': None,
                        'ru': None,
                        'created_at': datetime(70, 1, 1, 0, 0),
                        'upd_at': datetime(70, 1, 1, 0, 0)
                    }
