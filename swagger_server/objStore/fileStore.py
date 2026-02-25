import json
import logging
import os
from http import HTTPStatus

from swagger_server.models import Event, Program, Report, Resource, Subscription, Ven
from swagger_server.objStore.objStore import ObjStore

_TYPE_MAP = {
    'PROGRAM': ('programs', Program),
    'EVENT': ('events', Event),
    'REPORT': ('reports', Report),
    'SUBSCRIPTION': ('subscriptions', Subscription),
    'VEN': ('vens', Ven),
    'RESOURCE': ('resources', Resource),

    'BL_VEN_REQUEST': ('vens', Ven),
    'VEN_VEN_REQUEST': ('vens', Ven),

    'BL_RESOURCE_REQUEST': ('resources', Resource),
    'VEN_RESOURCE_REQUEST': ('resources', Resource),
}

_EMPTY_DATA = {key: [] for key in ('programs', 'events', 'reports', 'subscriptions', 'vens', 'resources')}


class FileStore(ObjStore):
    """
    ObjStore implementation that persists data to a JSON file.
    Each write serialises the full in-memory state; each read deserialises it.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.isfile(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._write(dict(_EMPTY_DATA))
        self.id_counter = self._max_existing_id()

    # ------------------------------------------------------------------
    # ObjStore interface
    # ------------------------------------------------------------------

    def insert(self, obj):
        logging.info(f"FileStore.insert(): obj={obj}")
        entry = self._get_list_and_cls(obj.object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, _ = entry

        data = self._read()
        self.id_counter += 1
        obj.id = str(self.id_counter)
        data[field].append(obj.to_json_dict())
        self._write(data)
        logging.debug(f"FileStore.insert(): assigned id={obj.id}")
        return HTTPStatus.CREATED

    def remove(self, object_type, id):
        logging.info(f"FileStore.remove(): object_type={object_type} id={id}")
        entry = self._get_list_and_cls(object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, cls = entry

        data = self._read()
        items = data[field]
        match = next((item for item in items if str(item.get('id')) == str(id)), None)
        if match is None:
            return HTTPStatus.NOT_FOUND
        items.remove(match)
        self._write(data)
        return cls.from_dict(match)

    def update(self, object_type, obj):
        logging.info(f"FileStore.update(): obj={obj}")
        entry = self._get_list_and_cls(object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, _ = entry

        data = self._read()
        items = data[field]
        idx = next((i for i, item in enumerate(items) if str(item.get('id')) == str(obj.id)), None)
        if idx is None:
            return HTTPStatus.NOT_FOUND
        items[idx] = obj.to_json_dict()
        self._write(data)
        logging.debug(f"FileStore.update(): updated index={idx}")
        return obj

    def search_all(self, object_type) -> list:
        logging.info(f"FileStore.search_all(): object_type={object_type}")
        entry = self._get_list_and_cls(object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, cls = entry

        data = self._read()
        return [cls.from_dict(item) for item in data[field]]

    def search(self, object_type, id):
        logging.info(f"FileStore.search(): object_type={object_type} id={id}")
        entry = self._get_list_and_cls(object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, cls = entry

        data = self._read()
        match = next((item for item in data[field] if str(item.get('id')) == str(id)), None)
        if match is None:
            return HTTPStatus.NOT_FOUND
        return cls.from_dict(match)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read(self) -> dict:
        logging.debug(f"FileStore._read(): path={self.file_path}")
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _write(self, data: dict):
        logging.debug(f"FileStore._write(): path={self.file_path}")
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _max_existing_id(self) -> int:
        """Return the highest numeric id already stored, so the counter never collides after a restart."""
        try:
            data = self._read()
        except (json.JSONDecodeError, OSError):
            return 0
        max_id = 0
        for items in data.values():
            if isinstance(items, list):
                for item in items:
                    try:
                        max_id = max(max_id, int(item.get('id', 0)))
                    except (TypeError, ValueError):
                        pass
        return max_id

    @staticmethod
    def _get_list_and_cls(object_type):
        entry = _TYPE_MAP.get(object_type)
        if entry is None:
            logging.warning(f"FileStore: unknown object_type={object_type}")
        return entry