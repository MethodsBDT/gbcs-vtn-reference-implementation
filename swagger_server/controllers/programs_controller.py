import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.program import Program  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscriptions  # noqa: E501
from swagger_server import util

programs = []
programID = 0


def create_program(body=None):  # noqa: E501
    """create a program

    Create a new program in the server. # noqa: E501

    :param body: program item to add.
    :type body: dict | bytes

    :rtype: List[Program]
    """
    logging.info(f"create_program():")
    programBody = None
    if connexion.request.is_json:
        programBody = Program.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_program(): programBody={programBody}")
    if programBody is None:
        return []

    global programID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    program = Program(
        id=programID,
        created_date_time=current_time,
        modification_date_time=None,
        program_name=programBody.program_name,
        program_long_name=programBody.program_long_name,
        retailer_name=programBody.retailer_name,
        retailer_long_name=programBody.retailer_long_name,
        program_type=programBody.program_type,
        country=programBody.country,
        principal_subdivision=programBody.principal_subdivision,
        time_zone_offset=programBody.time_zone_offset,
        interval_period=programBody.interval_period,
        program_descriptions=programBody.program_descriptions,
        binding_events=programBody.binding_events,
        local_price=programBody.local_price,
        payload_descriptors=programBody.payload_descriptors
    )

    # bump program ID
    programID += 1

    programs.append(program)
    logging.debug(f"create_program(): program={program}")

    # for subscription in subscriptions:
    #     resource = next((resource for resource in subscription.resource_operations if
    #                      "PROGRAM" in resource.resources and "CREATE" in resource.operations), None)
    #     if resource is not None:
    #         logging.debug(f"create_program(): resource={resource}")
    #         response = requests.post(resource.callback_url, json=json.dumps(program.to_dict()))
    #         if response.status_code != 200:
    #             logging.warning(f"create_program: callback response.status_code={response.status_code}")
    #

    callback("PROGRAM", "POST", program)

    return program

def callback(resourceName, operation, object):
    logging.info(f"callback(): resourceName={resourceName}, operation={operation}, object={object}")

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.resource_operations if
                         resourceName in resource.resources and operation in resource.operations), None)
        if resource is not None:
            logging.debug(f"callback(): resource={resource}")
            response = requests.post(resource.callback_url, json=json.dumps(object.to_dict()))
            if response.status_code != 200:
                logging.warning(f"callback: callback response.status_code={response.status_code}")

def delete_program(program_id):  # noqa: E501
    """delete a program

    Delete an existing program with the programID in path. # noqa: E501

    :param program_id: Numeric ID of the program object.
    :type program_id: int

    :rtype: List[Program]
    """
    logging.info(f"delete_program(): program_id={program_id}")
    program = next((program for program in programs if program.id == program_id), None)
    if program is not None:
        programs.remove(program)
        logging.debug(f"delete_program(): program={program}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "PROGRAM" in resource.resources and "DELETE" in resource.operations), None)
            if resource is not None:
                logging.debug(f"delete_program(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(program.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"delete_program: callback response.status_code={response.status_code}")

        return program
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_program(): problem={problem}")
        return problem


def search_all_programs(no_defaults=None, skip=None, limit=None):  # noqa: E501
    """searches all programs

    List all programs known to the server. Use no_defaults query param to view representation w no default values. Use skip and pagination query params to limit reponse size.  # noqa: E501

    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Program]
    """
    logging.info(f"search_all_programs(): ")
    logging.debug(f"search_all_programs(): programs={programs}")
    return programs


def search_program_by_program_id(program_id, no_defaults=None):  # noqa: E501
    """searches programs by program ID

    Fetch the program specified by the programID in path. Use no_defaults query param to view representation w no default values.  # noqa: E501

    :param program_id: Numeric ID of the program object.
    :type program_id: int
    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool

    :rtype: Program
    """
    logging.info(f"search_program_by_program_id(): program_id={program_id}")
    program = next((program for program in programs if program.id == program_id), None)
    logging.debug(f"search_program_by_program_id(): program={program}")
    return program


def update_program(program_id, body=None):  # noqa: E501
    """update a program

    Update an existing program with the programID in path. # noqa: E501

    :param program_id: Numeric ID of the program object.
    :type program_id: int
    :param body: program item to update.
    :type body: dict | bytes

    :rtype: List[Program]
    """
    logging.info(f"update_program(): program_id={program_id}")
    programBody = None
    if connexion.request.is_json:
        programBody = Program.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_program(): programBody={programBody}")
    if programBody is None:
        return None

    program = next((program for program in programs if program.id == program_id), None)
    if program is not None:
        programs.remove(program)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        program.modification_date_time = current_time

        if programBody.program_name is not None:
            program.program_name = programBody.program_name
        if programBody.program_long_name is not None:
            program.program_long_name = programBody.program_long_name
        if programBody.retailer_name is not None:
            program.retailer_name = programBody.retailer_name
        if programBody.retailer_long_name is not None:
            program.retailer_long_name = programBody.retailer_long_name
        if programBody.program_type is not None:
            program.program_type = programBody.program_type
        if programBody.country is not None:
            program.country = programBody.country
        if programBody.principal_subdivision is not None:
            program.principal_subdivision = programBody.principal_subdivision
        if programBody.time_zone_offset is not None:
            program.time_zone_offset = programBody.time_zone_offset
        if programBody.interval_period is not None:
            program.active_period = programBody.interval_period
        if programBody.program_descriptions is not None:
            program.program_descriptions = programBody.program_descriptions
        if programBody.binding_events is not None:
            program.binding_events = programBody.binding_events
        if programBody.local_price is not None:
            program.local_price = programBody.local_price
        if programBody.payload_descriptors is not None:
            program.payload_descriptors = programBody.payload_descriptors

        programs.append(program)
        logging.debug(f"update_program: program={program}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "PROGRAM" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_program(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(program.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_program: callback response.status_code={response.status_code}")

        return program

    return None
