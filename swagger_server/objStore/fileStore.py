import json
import logging
import os
import tempfile
import threading
from http import HTTPStatus

from config import CLEAN_START
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

_EMPTY_DATA = {'_counter': 0, **{key: [] for key in ('programs', 'events', 'reports', 'subscriptions', 'vens', 'resources')}}


class FileStore(ObjStore):
    """
    ObjStore implementation that persists data to a JSON file.
    Each write serialises the full in-memory state; each read deserialises it.
    The id counter is stored in the file under the '_counter' key so it
    survives restarts and is safe across threads (protected by a lock).
    """

    def __init__(self, file_path: str):
        self._lock = threading.Lock()
        self.file_path = file_path
        if CLEAN_START and os.path.isfile(file_path):
            logging.info(f"FileStore: CLEAN_START enabled, removing {file_path}")
            os.remove(file_path)
        if not os.path.isfile(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._write(dict(_EMPTY_DATA))

    # ------------------------------------------------------------------
    # ObjStore interface
    # ------------------------------------------------------------------

    def reset(self):
        logging.info(f"ListStore.reset():")
        self.__init__(self.file_path)

    def insert(self, obj):
        logging.info(f"FileStore.insert(): obj={obj}")
        entry = self._get_list_and_cls(obj.object_type)
        if entry is None:
            return HTTPStatus.BAD_REQUEST
        field, _ = entry

        with self._lock:
            data = self._read()
            counter = data.get('_counter', 0) + 1
            data['_counter'] = counter
            obj.id = str(counter)
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

        with self._lock:
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

        with self._lock:
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
        dir_name = os.path.dirname(self.file_path)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, self.file_path)
        except Exception:
            os.unlink(tmp_path)
            raise

    @staticmethod
    def _get_list_and_cls(object_type):
        entry = _TYPE_MAP.get(object_type)
        if entry is None:
            logging.warning(f"FileStore: unknown object_type={object_type}")
        return entry