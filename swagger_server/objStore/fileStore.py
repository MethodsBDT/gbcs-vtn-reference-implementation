import logging
import json
import os

import jsonpickle

from swagger_server.models import Subscription, Report, Program, Event, Ven, Resource
from swagger_server.objStore.objStore import ObjStore
from dataclasses import dataclass


def from_dict(dict_data):
    programs = []
    events = []
    reports = []
    subscriptions = []
    vens = []
    resources = []

    for program in dict_data['programs']:
        programs.append(Program.from_dict(program))
    for event in dict_data['events']:
        events.append(Event.from_dict(event))
    for report in dict_data['reports']:
        reports.append(Report.from_dict(report))
    for subscription in dict_data['subscriptions']:
        subscriptions.append(Subscription.from_dict(subscription))
    for ven in dict_data['vens']:
        vens.append(Ven.from_dict(ven))
    for resource in dict_data['resources']:
        resources.append(Resource.from_dict(resource))
    return DataModel(programs, events, reports, subscriptions, vens, resources)


@dataclass
class DataModel:
    """Model for data"""

    def __init__(self, programs, events, reports, subscriptions, vens, resources):
        self.programs = programs
        self.events = events
        self.reports = reports
        self.subscriptions = subscriptions
        self.vens = vens
        self.resources = resources

    def to_json(self):
        # Event(**jsonpickle.decode(jsonpickle.encode(jsonpickle.decode(read).events[0].to_dict())))

        # json_data = jsonpickle.encode(self)
        # logging.info(json_data)

        return jsonpickle.encode({
            'programs': self.to_dict(self.programs),
            'events': self.to_dict(self.events),
            'reports': self.to_dict(self.reports),
            'subscriptions': self.to_dict(self.subscriptions),
            'vens': self.to_dict(self.vens),
            'resources': self.to_dict(self.resources)
        })

    def to_dict(self, list: list):
        result = []
        for item in list:
            result.append(item.to_dict())
        return result


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
            read = f.read()
            data = from_dict(jsonpickle.decode(read))
            return data

    def __write_file(self, data: DataModel):
        with open(self.file_path, "w+") as f:
            json_data = data.to_json()
            f.write(json_data)

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

    def search_all(self, object_type) -> list:
        logging.info(f"FileStore.search_all(): object_type={object_type}")
        saved_data = self.__read_file()
        return __get_type__(object_type, saved_data)

    def search(self, object_type, id):
        logging.info(f"FileStore.search(): object_type={object_type}, id={id}")
        saved_data = self.__read_file()
        _list = __get_type__(object_type, saved_data)
        logging.debug(f"FileStore.search(): list={_list}")
        return next((obj for obj in _list if str(obj.id) == str(id)), 404)


def __get_type__(object_type, data_model: DataModel) -> list:
    return {
        'PROGRAM': data_model.programs,
        'EVENT': data_model.events,
        'REPORT': data_model.reports,
        'SUBSCRIPTION': data_model.subscriptions,
        'VEN': data_model.vens,
        'RESOURCE': data_model.resources,
    }.get(object_type, 400)
