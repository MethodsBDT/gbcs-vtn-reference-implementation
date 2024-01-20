import connexion
from datetime import datetime
from http import HTTPStatus
import logging

from swagger_server import util
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.models.event import Event  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.objStore.storageInterface import objStore


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
    # if eventBody is None:
    #     problem = Problem(title="Bad Request: No request body", status="400")
    #     logging.warning(f"create_event(): problem={problem}")
    #     return problem, 400

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    event = Event(
        created_date_time=current_time,
        modification_date_time=None,
        object_type='EVENT',
        program_id=eventBody.program_id,
        event_name=eventBody.event_name,
        priority=eventBody.priority,
        targets=eventBody.targets,
        report_descriptors=eventBody.report_descriptors,
        payload_descriptors=eventBody.payload_descriptors,
        interval_period=eventBody.interval_period,
        intervals=eventBody.intervals
    )

    status = objStore.insert(event)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_event(): problem={problem}")
        return problem, status

    subscription_callback("EVENT", "POST", event)

    return event, status


def delete_event(event_id):  # noqa: E501
    """delete an event

    Delete the event specified by the eventID in path.  # noqa: E501

    :param event_id: object ID of event.
    :type event_id: dict | bytes

    :rtype: Event
    """
    logging.info(f"delete_event():")

    event = objStore.remove("EVENT", event_id)
    if type(event) is not Event:
        status = event
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_event(): problem={problem}")
        return problem, status

    subscription_callback("EVENT", "DELETE", event)

    return event, HTTPStatus.OK


def search_all_events(program_id=None, target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501
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
    logging.info(
        f"search_all_events(): program_id={program_id} target_type={target_type} target_values={target_values} skip={skip} limit={limit}")

    events = objStore.search_all("EVENT")
    logging.debug(f"search_all_events(): events={events}")
    if type(events) is not list:
        status = events
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_events(): problem={problem}")
        return problem, status

    logging.debug(f"search_all_events(): events={events}")
    eventList = events
    if program_id != None:
        # strip leading [' and tailing ']
        # program_id = program_id[2:-2]
        eventList = [event for event in events if event.program_id == program_id]
        if len(eventList) == 0:
            return eventList, HTTPStatus.OK
    eventList = util.getTargets(eventList, target_type, target_values)
    if skip != None:
        if len(events) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_events(): problem={problem}")
            return problem, HTTPStatus.NOT_FOUND
        eventList = events[skip:]
    if limit != None:
        eventList = eventList[:limit]

    subscription_callback("EVENT", "GET", eventList)

    return eventList


def search_events_by_id(event_id):  # noqa: E501
    """search events by ID

    Fetch event associated with the eventID in path.   # noqa: E501

    :param event_id: object ID of event.
    :type event_id: dict | bytes

    :rtype: List[Event]
    """
    logging.info(f"search_events_by_id(): event_id={event_id}")
    event = objStore.search("EVENT", event_id)
    if type(event) is not Event:
        status = event
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_events_by_id(): problem={problem}")
        return problem, status
    logging.debug(f"search_events_by_id(): event={event}")

    subscription_callback("EVENT", "GET", event)

    return event, HTTPStatus.OK


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
        problem = Problem(title="Bad Request: No request body", status="400")
        logging.warning(f"update_event(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST

    event, status = search_events_by_id(event_id)
    if event is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: program_id not found", status="404")
        logging.warning(f"update_event(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    event.modification_date_time = current_time

    if eventBody.program_id != event.program_id:
        problem = Problem(title="Bad Request: program ID cannot be modified", status="400")
        return problem, HTTPStatus.BAD_REQUEST
    if eventBody.event_name is not None:
        event.event_name = eventBody.event_name
    if eventBody.priority is not None:
        event.priority = eventBody.priority
    if eventBody.targets is not None:
        event.targets = eventBody.targets
    if eventBody.report_descriptors is not None:
        event.report_requests = eventBody.report_descriptors
    if eventBody.payload_descriptors is not None:
        event.payload_descriptors = eventBody.payload_descriptors
    if eventBody.interval_period is not None:
        event.interval_period = eventBody.interval_period
    if eventBody.intervals is not None:
        event.intervals = eventBody.intervals

    event = objStore.update("EVENT", event)
    if type(event) is not Event:
        status = event
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_event(): problem={problem}")
        return problem, status
    logging.debug(f"update_event(): event={event}")

    subscription_callback("EVENT", "PUT", event)

    return event, HTTPStatus.OK
