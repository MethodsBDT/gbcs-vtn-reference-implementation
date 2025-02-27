from http import HTTPStatus
import logging
from swagger_server.objStore.objStore import ObjStore

programs = []
programID = 0

events = []
eventID = 0

reports = []
reportID = 0

subscriptions = []
subscriptionID = 0

vens = []
venID = 0

resourceIDs = [0]
# TBD remove as resources are stored in body of ven
resources = []


class ListStore(ObjStore):
    """
    object store list implementation

    methods return http status codes
    """

    def __init__(self):
        logging.info(f"ListStore.__init__():")

    def insert(self, obj):
        logging.info(f"ListStore.insert(): obj={obj}")
        logging.debug(f"ListStore.insert(): obj.object_type={obj.object_type}")

        if obj.object_type == 'PROGRAM':
            list = programs
            global programID
            id = programID
            programID += 1
        elif obj.object_type == 'EVENT':
            list = events
            global eventID
            id = eventID
            eventID += 1
        elif obj.object_type == 'REPORT':
            list = reports
            global reportID
            id = reportID
            reportID += 1
        elif obj.object_type == 'SUBSCRIPTION':
            list = subscriptions
            global subscriptionID
            id = subscriptionID
            subscriptionID += 1
        elif obj.object_type == 'VEN':
            list = vens
            global venID
            id = venID
            venID += 1
        elif obj.object_type == 'RESOURCE':
            list = resources
            global resourceID
            id = resourceID
            resourceID += 1
        else:
            logging.warning(f"ListStore.insert(): unknown obj.object_type={obj.object_type}")
            return HTTPStatus.BAD_REQUEST

        #
        logging.debug(f"ListStore.insert(): list={list}")

        obj.id = str(id)

        list.append(obj)

        return HTTPStatus.CREATED

    def remove(self, object_type, id):
        logging.info(f"ListStore.remove(): object_type={object_type} id={id}")

        if object_type == 'PROGRAM':
            list = programs
        elif object_type == 'EVENT':
            list = events
        elif object_type == 'REPORT':
            list = reports
        elif object_type == 'SUBSCRIPTION':
            list = subscriptions
        elif object_type == 'VEN':
            list = vens
        elif object_type == 'RESOURCE':
            list = resources
        else:
            logging.warning(f"ListStore.remove(): unknown obj.object_type={object_type}")
            return HTTPStatus.BAD_REQUEST

        object = next((obj for obj in list if str(obj.id) == str(id)), None)

        if object is not None:
            list.remove(object)
            logging.debug(f"ListStore.remove(): object={object}")
            return object
        else:
            return HTTPStatus.NOT_FOUND

    def update(self, object_type, obj):
        logging.info(f"ListStore.update():: obj={obj}")
        if object_type == 'PROGRAM':
            list = programs
        elif object_type == 'EVENT':
            list = events
        elif object_type == 'REPORT':
            list = reports
        elif object_type == 'SUBSCRIPTION':
            list = subscriptions
        elif object_type == 'VEN':
            list = vens
        elif object_type == 'RESOURCE':
            list = resources
        else:
            logging.warning(f"ListStore.update(): unknown obj.object_type={object_type}")
            return HTTPStatus.BAD_REQUEST

        object = next((object for object in list if str(object.id) == str(obj.id)), None)
        if object is not None:
            logging.debug(f"ListStore.update(): original object={object}")

            index = list.index(object)
            list[index] = object

            logging.debug(f"ListStore.update(): list[index]={list[index]}")
            return object
        else:
            return HTTPStatus.NOT_FOUND

    def search_all(self, object_type):
        logging.info(f"ListStore.search_all(): object_type={object_type}")
        if object_type == 'PROGRAM':
            return programs
        elif object_type == 'EVENT':
            return events
        elif object_type == 'REPORT':
            return reports
        elif object_type == 'SUBSCRIPTION':
            return subscriptions
        elif object_type == 'VEN':
            return vens
        elif object_type == 'RESOURCE':
            return resources
        else:
            logging.warning(f"ListStore.search_all(): unknown object_type={object_type}")
            return HTTPStatus.BAD_REQUEST

    def search(self, object_type, id):
        logging.info(f"ListStore.search(): object_type={object_type}, id={id}")

        if object_type == 'PROGRAM':
            list = programs
        elif object_type == 'EVENT':
            list = events
        elif object_type == 'REPORT':
            list = reports
        elif object_type == 'SUBSCRIPTION':
            list = subscriptions
        elif object_type == 'VEN':
            list = vens
        elif object_type == 'RESOURCE':
            list = resources
        else:
            logging.warning(f"ListStore.remove(): unknown obj.object_type={object_type}")
            return HTTPStatus.BAD_REQUEST

        logging.debug(f"ListStore.search(): list={list}")
        return next((obj for obj in list if str(obj.id) == str(id)), 404)
