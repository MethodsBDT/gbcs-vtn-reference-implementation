from config import STORAGE_IMPLEMENTATION
from swagger_server.objStore.listStore import ListStore
from swagger_server.objStore.fileStore import FileStore
from swagger_server.objStore.objStore import ObjStore


class StorageInterface(ObjStore):

    def __init__(self):
        self.storage = {
            'IN_MEMORY': ListStore(),
            'IN_FILE_TMP': FileStore(),
        }[STORAGE_IMPLEMENTATION]

    def insert(self, obj):
        self.storage.insert(obj)

    def remove(self, object_type, id):
        self.storage.remove(object_type, id)

    def update(self, object_type, obj):
        self.storage.update(object_type, obj)

    def search_all(self, object_type):
        self.storage.search_all(object_type)

    def search(self, object_type, id):
        self.storage.search_all(object_type, id)


objStore = StorageInterface()
