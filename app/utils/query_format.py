from typing import Optional

from core.dal import PropsManager
from core.models import FilterObj


async def serialize_query(filter_map: FilterObj, manager: PropsManager) -> dict:
    ranges = await _fetch_ranges_depends(manager)
    serializer = Serializer(filter_map, ranges)
    return serializer.serialize


async def _fetch_ranges_depends(manager: PropsManager) -> dict:
    return await manager.fetch_all_ranges()


class Serializer:
    def __init__(self, filter_map: FilterObj, ranges: dict):
        self._filter_map = filter_map
        self._ranges = ranges

    @property
    def serialize(self) -> Optional[dict]:
        filter_set = []
        filter_map = {'$and': filter_set}
        obj_attrs = vars(self._filter_map)
        for key in obj_attrs:
            if value := obj_attrs.get(key):
                if key == 'title':
                    filter_set.append(self._serialize_title(value))
                elif key == 'id':
                    filter_set.append(self._serialize_id(value))
                elif key in ('region', 'type'):
                    filter_set.append(self._serialize_param(key, value))
                else:
                    filter_set.append(self._serialize_array_param(key, value))
        if filter_set:
            return filter_map

    @staticmethod
    def _serialize_id(value: str) -> dict:
        regex = {"$regex": f"^{value}", "$options": "i"}
        val_filter = {
            '_id': regex
        }
        return val_filter

    @staticmethod
    def _serialize_title(value: str) -> dict:
        regex = {"$regex": f".*{value}.*", "$options": "i"}
        val_filter = {
            "$or": [
                {'en.title': regex},
                {'de.title': regex},
                {'ru.title': regex}
            ]
        }
        return val_filter

    @staticmethod
    def _serialize_param(key: str, value: str) -> dict:
        val_filter = {f"property.{key}": value}
        return val_filter

    def _serialize_array_param(self, key: str, value: list) -> dict:
        if value:
            val_filter = None
            ranges = self._ranges
            range_value = ranges.get(key)
            for i in range(2):
                if range_value and value[i] == range_value[i]:
                    val_filter = {"$or":
                        [
                            {f"property.{key}": {"$gte": value[0], "$lte": value[1]}},
                            {f"property.{key}": {"$exists": False}}
                        ]
                    }
                else:
                    val_filter = {f"property.{key}": {"$gte": value[0], "$lte": value[1]}}
            return val_filter
