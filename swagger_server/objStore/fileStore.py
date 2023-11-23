import logging
import json
from swagger_server.objStore.objStore import ObjStore


class DataModel:

    def __init__(self, programs: list[dict], events: list[dict], reports: list[dict], subscriptions: list[dict],
                 vens: list[dict], resources: list[dict]):
        self.programs = programs
        self.events = events
        self.reports = reports
        self.subscriptions = subscriptions
        self.vens = vens
        self.resources = resources


class FileStore(ObjStore):
    """
    abstract class defines interface to object storage implementations, such as simple lists
    or database interfaces like SQLAlchemy
    """

    def __init__(self):
        self.file_path = "./tmp/fileStorage.json"

    def insert(self, obj):
        data_model = self.__read_file()
        __get_type__(obj.object_type, data_model).insert(obj, __object=obj)
        self.__write_file(data_model)
        return []

    def remove(self, objType, id):
        data_model = self.__read_file()

        self.__write_file(data_model)
        return []

    def update(self, objType, obj):
        data_model = self.__read_file()

        self.__write_file(data_model)
        return []

    def search_all(self, objType):
        data_model = self.__read_file()
        return []

    def search(self, objType, id):
        data_model = self.__read_file()
        return []

    def __read_file(self) -> DataModel:
        with open(self.file_path, "r+") as f:
            data = json.loads(f.read())
            return DataModel(**data)

    def __write_file(self, data: DataModel):
        with open(self.file_path, "w+") as f:
            f.write(json.dumps(data))


def __get_type__(objType, data_model: DataModel) -> list[dict]:
    return {
        'PROGRAM': data_model.programs,
        'EVENT': data_model.events,
        'REPORT': data_model.reports,
        'SUBSCRIPTION': data_model.subscriptions,
        'VEN': data_model.vens,
        'RESOURCE': data_model.resources,
    }[objType](data_model)


objStore = FileStore()
