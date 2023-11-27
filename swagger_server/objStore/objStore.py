
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
    def remove(self, object_type, id):
        pass

    @abstractmethod
    def update(self, object_type, obj):
        pass

    @abstractmethod
    def search_all(self, object_type):
        pass

    @abstractmethod
    def search(self, object_type, id):
        pass
