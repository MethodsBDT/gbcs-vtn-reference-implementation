import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.event import Event  # noqa: E501
from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.target import Target  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server import util

events = []
eventID = 0


def create_event(body=None):  # noqa: E501
    """create an event

    Create a new event in the server. # noqa: E501

    :param body: Event item to add.
    :type body: dict | bytes

    :rtype: Event
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
        id=str(eventID),
        created_date_time=current_time,
        modification_date_time=None,
        program_id=eventBody.program_id,
        event_name=eventBody.event_name,
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

    subscription_callback("EVENT", "POST", event)

    return event


def delete_event(event_id):  # noqa: E501
    """delete an event

    Delete the event specified by the eventID in path.  # noqa: E501

    :param event_id: object ID of event.
    :type event_id: dict | bytes

    :rtype: Event
    """
    logging.info(f"delete_event():")

    event = next((event for event in events if event.id == event_id), None)
    if event is not None:
        events.remove(event)
        logging.debug(f"delete_event(): event={event}")

        subscription_callback("EVENT", "DELETE", event)

        return event
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_event: problem={problem}")
        return problem, 404


def search_all_events(program_id=None, targets=None, skip=None, limit=None):  # noqa: E501
    """searches all events

    List all events known to the server. May filter results by programID query param. Use skip and pagination query params to limit reponse size.  # noqa: E501

    :param program_id: filter results to events with programID.
    :type program_id: dict | bytes
    :param targets: return programs that match requested targets
    :type targets: list | bytes
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

    return eventList


def search_events_by_id(event_id):  # noqa: E501
    """search events by ID

    Fetch event associated with the eventID in path.   # noqa: E501

    :param event_id: object ID of event.
    :type event_id: dict | bytes

    :rtype: List[Event]
    """
    logging.info(f"search_events_by_id(): event_id={event_id}")
    event = next((event for event in events if event.id == event_id), None)
    logging.debug(f"search_events_by_id(): event={event}")

    return event


def update_event(event_id, body=None):  # noqa: E501
    """update an event

    Update the event specified by the eventID in path. # noqa: E501

    :param event_id: object ID of event.
    :type event_id: dict | bytes
    :param body: event item to update.
    :type body: dict | bytes

    :rtype: Event
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
            return problem, 400
        if eventBody.event_name is not None:
            event.event_name = eventBody.event_name
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

        subscription_callback("EVENT", "PUT", event)

        return (event)

    return None
