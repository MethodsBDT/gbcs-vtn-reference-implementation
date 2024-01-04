import connexion
from datetime import datetime
import logging

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.program import Program  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.objStore.storageInterface import objStore
from swagger_server import util

def create_program(body=None):  # noqa: E501
    """create a program

    Create a new program in the server. # noqa: E501

    :param body: program item to add.
    :type body: dict | bytes

    :rtype: Program
    """
    logging.info(f"create_program():")

    programBody = None
    if connexion.request.is_json:
        programBody = Program.from_dict(connexion.request.get_json())  # noqa: E501
        # logging.debug(f"create_program(): programBody={programBody}")
    # TBD: is this necessary or handled by framework?
    # if programBody is None:
    #     problem = Problem(title="Bad Request: No request body", status="400")
    #     logging.warning(f"create_program(): problem={problem}")
    #     return problem, 400

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    program = Program(
        created_date_time=current_time,
        modification_date_time=None,
        object_type='PROGRAM',
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
        payload_descriptors=programBody.payload_descriptors,
        targets = programBody.targets
    )

    status = objStore.insert(program)
    if status != 200:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_program(): problem={problem}")
        return problem, status

    logging.debug(f"create_program(): program={program}")

    subscription_callback("PROGRAM", "POST", program)

    return program, status

def delete_program(program_id):  # noqa: E501
    """delete a program

    Delete an existing program with the programID in path. # noqa: E501

    :param program_id: Object ID of the program object.
    :type program_id: dict | bytes

    :rtype: Program
    """
    logging.info(f"delete_program(): program_id={program_id}")

    program = objStore.remove("PROGRAM", program_id)
    if type(program) is not Program:
        status = program
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_program(): problem={problem}")
        return problem, status

    # TBD: need to test if this is not present
    subscription_callback("PROGRAM", "DELETE", program)

    return program, 200

def search_all_programs(target_type=None, target_values=None, skip=None, limit=None):  # noqa: E501

    """searches all programs

    List all programs known to the server. Use skip and pagination query params to limit response size.  # noqa: E501

    :param target_type: Indicates targeting type, e.g. GROUP
    :type target_type: str
    :param target_values: List of target values, e.g. group names
    :type target_values: List[str]
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Program]
    """
    logging.info(f"search_all_programs(): target_type={target_type} target_values={target_values} skip={skip} limit={limit}")

    programs = objStore.search_all("PROGRAM")
    if type(programs) is not list:
        status = programs
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_programs(): problem={problem}")
        return problem, status
    
    logging.debug(f"search_all_programs(): programs={programs}")
    programList = util.getTargets(programs, target_type, target_values)
    if skip != None:
        if len(programs) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_programs(): problem={problem}")
            return problem, 404
        programList = programs[skip:]
    if limit != None:
        programList = programList[:limit]
    logging.debug(f"search_all_programs(): programList={programList}")

    subscription_callback("PROGRAM", "GET", programList)

    return programList, 200


def search_program_by_program_id(program_id):  # noqa: E501
    """searches programs by program ID

    Fetch the program specified by the programID in path.  # noqa: E501

    :param program_id: Object ID of the program object.
    :type program_id: dict | bytes

    :rtype: Program
    """
    logging.info(f"search_program_by_program_id(): program_id={program_id}")

    program = objStore.search("PROGRAM", program_id)
    if type(program) is not Program:
        status = program
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_program_by_program_id(): problem={problem}")
        return problem, status

    logging.debug(f"search_program_by_program_id(): program={program}")

    subscription_callback("PROGRAM", "GET", program)

    return program, 200

def update_program(program_id, body=None):  # noqa: E501
    """update a program

    Update an existing program with the programID in path. # noqa: E501

    :param program_id: Object ID of the program object.
    :type program_id: dict | bytes
    :param body: program item to update.
    :type body: dict | bytes

    :rtype: Program
    """
    logging.info(f"update_program(): program_id={program_id}")
    programBody = None
    if connexion.request.is_json:
        programBody = Program.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_program(): programBody={programBody}")
    # if programBody is None:
    #     problem = Problem(title="Bad Request: No request body", status="400")
    #     logging.warning(f"update_program(): problem={problem}")
    #     return problem, 400

    program, status = search_program_by_program_id(program_id)
    if program is None or status == 404:
        problem = Problem(title="Not Found: program_id not found", status="404")
        logging.warning(f"update_program(): problem={problem}")
        return problem, 404

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
    if programBody.targets is not None:
        program.targets = programBody.targets

    program = objStore.update("PROGRAM", program)
    if type(program) is not Program:
        status = program
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_program(): problem={problem}")
        return problem, status

    logging.debug(f"update_program: program={program}")

    subscription_callback("PROGRAM", "PUT", program)

    return program, 200

