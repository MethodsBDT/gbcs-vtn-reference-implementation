from __future__ import annotations

import logging
import json
import os

import jsonpickle

from swagger_server.models import Subscription, Report, Program, Event, Ven, Resource
from swagger_server.objStore.objStore import ObjStore
from dataclasses import dataclass


@dataclass
class DataModel:
    """Model for data"""
    programs: list[Program]
    events: list[Event]
    reports: list[Report]
    subscriptions: list[Subscription]
    vens: list[Ven]
    resources: list[Resource]

    def to_json(self):
        json_data = jsonpickle.encode(self)
        logging.info(json_data)
        return json_data


class FileStore(ObjStore):
    """
    abstract class defines interface to object storage implementations, such as simple lists
    or database interfaces like SQLAlchemy
    """

    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.isfile(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.__write_file(DataModel([], [], [], [], [], []))
        self.id_counter = 0

    def __read_file(self) -> DataModel:
        with open(self.file_path, "r+") as f:
            data = jsonpickle.decode(f.read())
            print(f'Read: {data}')
            return data

    def __write_file(self, data: DataModel):
        with open(self.file_path, "w+") as f:
            data = data.to_json()
            print(f'Write: {data}')
            f.write(data)

    def insert(self, obj):
        object_type = obj.object_type
        logging.info(f"FileStore.insert(): obj={obj}")
        logging.debug(f"FileStore.insert(): obj.object_type={object_type}")
        saved_data = self.__read_file()
        _list = __get_type__(object_type, saved_data)
        logging.debug(f"FileStore.insert(): list={_list}")
        self.id_counter = self.id_counter + 1
        counter = self.id_counter
        obj.id = str(counter)
        _list.append(obj)
        self.__write_file(saved_data)
        return 200

    def remove(self, object_type, id):
        logging.info(f"FileStore.remove(): object_type={object_type} id={id}")
        saved_data = self.__read_file()
        _list = __get_type__(object_type, saved_data)
        _object = next((obj for obj in _list if str(obj.id) == str(id)), None)
        if _object is not None:
            _list.remove(_object)
            logging.debug(f"FileStore.remove(): object={_object}")
            self.__write_file(saved_data)
            return _object
        else:
            return 404

    def update(self, object_type, obj):
        logging.info(f"FileStore.update():: obj={obj}")
        saved_data = self.__read_file()
        _list = __get_type__(object_type, saved_data)
        _object = next((object for object in _list if str(object.id) == str(obj.id)), None)
        if _object is not None:
            logging.debug(f"FileStore.update(): original object={_object}")
            index = _list.index(_object)
            _list[index] = _object
            logging.debug(f"FileStore.update(): list[{index}]={_list[index]}")
            _list.append(_object)
            self.__write_file(saved_data)
            logging.info(saved_data)
            return _object
        else:
            return 404

    def search_all(self, object_type) -> list[Subscription] | list[Report] | list[Program] | list[Event] | \
                                         list[Ven] | list[Resource] | int:
        logging.info(f"FileStore.search_all(): object_type={object_type}")
        saved_data = self.__read_file()
        return __get_type__(object_type, saved_data)


    def search(self, object_type, id) -> Subscription | Report | Program | Event | Ven | Resource | int:
        logging.info(f"FileStore.search(): object_type={object_type}, id={id}")
        saved_data = self.__read_file()
        _list = __get_type__(object_type, saved_data)
        logging.debug(f"FileStore.search(): list={_list}")
        return next((obj for obj in _list if str(obj.id) == str(id)), 404)


def __get_type__(object_type, data_model: DataModel) -> list[Subscription] | list[Report] | list[Program] | list[
    Event] | list[Ven] | list[Resource] | int:
    return {
        'PROGRAM': data_model.programs,
        'EVENT': data_model.events,
        'REPORT': data_model.reports,
        'SUBSCRIPTION': data_model.subscriptions,
        'VEN': data_model.vens,
        'RESOURCE': data_model.resources,
    }.get(object_type, 400)
