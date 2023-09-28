
from abc import ABC, abstractmethod

class ObjStore(ABC):
    """
    abstract class defines interface to object storage implementations, such as simple lists
    or database interfaces like SQLAlchemy
    """

    @abstractmethod
    def insert(self, obj):
        pass

    @abstractmethod
    def remove(self, objType, id):
        pass

    @abstractmethod
    def update(self, objType, obj):
        pass

    @abstractmethod
    def search_all(self, objType):
        pass

    @abstractmethod
    def search(self, objType, id):
        pass
