import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscriptions  # noqa: E501
from swagger_server import util

events = []
eventID = 0


def create_event(body=None):  # noqa: E501
    """create an event

    Create a new event in the server. # noqa: E501

    :param body: Event item to add.
    :type body: dict | bytes

    :rtype: List[Event]
    """
    logging.info(f"create_event():")

    eventBody = None
    if connexion.request.is_json:
        eventBody = Event.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_event(): eventBody={eventBody}")
    if eventBody is None:
        return []

    global eventID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    event = Event(
        id=eventID,
        created_date_time=current_time,
        modification_date_time=None,
        program_id=eventBody.program_id,
        name=eventBody.name,
        priority=eventBody.priority,
        targets=eventBody.targets,
        report_descriptors=eventBody.report_descriptors,
        interval_period=eventBody.interval_period,
        intervals=eventBody.intervals
    )

    # bump event ID
    eventID += 1

    events.append(event)
    logging.debug(f"create_event(): event={event}")

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.resource_operations if "EVENT" in resource.resources and "POST" in resource.operations), None)
        if resource is not None:
            logging.debug(f"create_event(): resource={resource}")
            response = requests.post(resource.callback_url, json=json.dumps(event.to_dict()))
            if response.status_code != 200:
                logging.warning(f"create_event: callback response.status_code={response.status_code}")

    return event


def delete_event(event_id):  # noqa: E501
    """delete an event

    Delete the event specified by the eventID in path.  # noqa: E501

    :param event_id: event ID.
    :type event_id: int

    :rtype: List[Event]
    """
    logging.info(f"delete_event():")

    event = next((event for event in events if event.id == event_id), None)
    if event is not None:
        events.remove(event)
        logging.debug(f"delete_event(): event={event}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "EVENT" in resource.resources and "DELETE" in resource.operations), None)
            if resource is not None:
                logging.debug(f"delete_event(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(event.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"delete_event: callback response.status_code={response.status_code}")

        return event
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_event: problem={problem}")
        return problem


def search_all_events(program_id=None, no_defaults=None, skip=None, limit=None):  # noqa: E501
    """searches all events

    List all events known to the server. May filter results by programID query param. Use skip and pagination query params to limit reponse size. Use no_defaults query param to view represenation w no default values.  # noqa: E501

    :param program_id: Numeric ID of the associated program.
    :type program_id: int
    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Event]
    """
    logging.info(f"search_all_events(): program_id={program_id}")

    eventList = events
    if program_id is not None:
        tempEvents = [event for event in events if event.program_id == program_id]
        logging.debug(f"search_all_events(): tempEvents={tempEvents}")
        eventList = tempEvents

    if no_defaults == True:
        noneEvents = []
        for tempEvent in eventList:
            noneEvents.append(util.remove_none(tempEvent))
        eventList = noneEvents

    return eventList


def search_events_by_id(event_id, no_defaults=None):  # noqa: E501
    """search events by ID

    Fetch event associated with the eventID in path. Use no_defaults query param to view representation w no default values.  # noqa: E501

    :param event_id: event ID.
    :type event_id: int
    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool

    :rtype: List[Event]
    """
    logging.info(f"search_events_by_id(): event_id={event_id}")
    event = next((event for event in events if event.id == event_id), None)
    logging.debug(f"search_events_by_id(): event={event}")

    if event is not None and no_defaults == True:
        event = util.remove_none(event)

    return event


def update_event(event_id, body=None):  # noqa: E501
    """update an event

    Update the event specified by the eventID in path. # noqa: E501

    :param event_id: event ID.
    :type event_id: int
    :param body: event item to update.
    :type body: dict | bytes

    :rtype: List[Event]
    """
    logging.info(f"update_event(): event_id={event_id}")

    eventBody = None
    if connexion.request.is_json:
        eventBody = Event.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_event(): eventBody={eventBody}")
    if eventBody is None:
        return []

    event = next((event for event in events if event.id == event_id), None)
    if event is not None:
        events.remove(event)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        event.modification_date_time = current_time

        if eventBody.program_id != event.program_id:
            problem = Problem(title="Bad Request: program ID cannot be modified", status="400")
            return problem
        if eventBody.name is not None:
            event.name = eventBody.name
        if eventBody.priority is not None:
            event.priority = eventBody.priority
        if eventBody.targets is not None:
            event.targets = eventBody.targets
        if eventBody.report_descriptors is not None:
            event.report_requests = eventBody.report_descriptors
        if eventBody.interval_period is not None:
            event.interval_period = eventBody.interval_period
        if eventBody.intervals is not None:
            event.intervals = eventBody.intervals

        events.append(event)
        logging.debug(f"update_event(): event={event}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "EVENT" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_event(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(event.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_event: callback response.status_code={response.status_code}")

        return (event)

    return None
