from config import STORAGE_IMPLEMENTATION, STORAGE_FILE_PATH
from swagger_server.objStore.listStore import ListStore
from swagger_server.objStore.fileStore import FileStore
from swagger_server.objStore.objStore import ObjStore


class StorageInterface(ObjStore):

    def __init__(self):
        self.storage = {
            # use lambda to not initialize all repositories
            'IN_MEMORY': lambda x: ListStore(),
            'IN_FILE': lambda x: FileStore(file_path=STORAGE_FILE_PATH),
        }.get(STORAGE_IMPLEMENTATION, 'IN_MEMORY')('')

    def insert(self, obj):
        return self.storage.insert(obj)

    def remove(self, object_type, id):
        return self.storage.remove(object_type, id)

    def update(self, object_type, obj):
        return self.storage.update(object_type, obj)

    def search_all(self, object_type):
        return self.storage.search_all(object_type)

    def search(self, object_type, id):
        return self.storage.search(object_type, id)

    def reset(self):
        return self.storage.reset()

objStore = StorageInterface()
