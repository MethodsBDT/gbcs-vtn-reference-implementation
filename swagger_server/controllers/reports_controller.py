import connexion
from datetime import datetime
import json
import logging
import requests
import six

from swagger_server.models.report import Report  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscriptions  # noqa: E501
from swagger_server import util

reports = []
reportID = 0


def create_report(body=None):  # noqa: E501
    """add a report

    Create a new report in the server. # noqa: E501

    :param body: report item to add.
    :type body: dict | bytes

    :rtype: List[Report]
    """
    logging.info(f"create_report():")
    reportBody = None
    if connexion.request.is_json:
        reportBody = Report.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_report(): reportBody={reportBody}")
    if reportBody is None:
        return []

    global reportID
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    report = Report(
        id=reportID,
        created_date_time=current_time,
        modification_date_time=None,
        program_id=reportBody.program_id,
        event_id=reportBody.event_id,
        client_id=reportBody.client_id,
        name=reportBody.name,
        payload_descriptors=reportBody.payload_descriptors,
        resources=reportBody.resources
    )

    # bump report ID
    reportID += 1

    reports.append(report)
    logging.debug(f"create_report(): report={report}")

    for subscription in subscriptions:
        resource = next((resource for resource in subscription.resource_operations if
                         "REPORT" in resource.resources and "POST" in resource.operations), None)
        if resource is not None:
            logging.debug(f"create_report(): resource={resource}")
            response = requests.post(resource.callback_url, json=json.dumps(event.to_dict()))
            if response.status_code != 200:
                logging.warning(f"create_report: callback response.status_code={response.status_code}")

    return report


def delete_report(report_id):  # noqa: E501
    """delete a report

    Delete the program specified by the reportID in path. # noqa: E501

    :param report_id: Numeric ID of a report.
    :type report_id: int

    :rtype: List[Report]
    """
    logging.info(f"delete_report(): report_id={report_id}")
    report = next((report for report in reports if report.id == report_id), None)
    if report is not None:
        reports.remove(report)
        logging.debug(f"delete_report(): report={report}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "REPORT" in resource.resources and "DELETE" in resource.operations), None)
            if resource is not None:
                logging.debug(f"delete_report(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(event.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"delete_report: callback response.status_code={response.status_code}")

        return report
    else:
        problem = Problem(title="Not Found", status="404")
        logging.warning(f"delete_report(): problem={problem}")
        return problem


def search_all_reports(program_id=None, client_id=None, no_defaults=None, skip=None, limit=None):  # noqa: E501
    """searches all reports

    List all reports known to the server. May filter results by programID and clientID as query param. Use no_defaults query param to view representation w no default values. Use skip and pagination query params to limit reponse size.  # noqa: E501

    :param program_id: Numeric ID of the associated program.
    :type program_id: int
    :param client_id: Numeric ID of the associated program.
    :type client_id: int
    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Report]
    """
    logging.info(f"search_all_reports(): program_id={program_id}")
    if program_id is not None:
        tempreports = [report for report in reports if report.program_id == program_id]
        logging.debug(f"search_all_reports(): tempreports={tempreports}")
        return tempreports
    return reports

def search_reports_by_report_id(report_id, no_defaults=None):  # noqa: E501
    """searches reports by reportID

    Fetch the report specified by the reportID in path. Use no_defaults query param to view representation w no default values.  # noqa: E501

    :param report_id: Numeric ID of a report.
    :type report_id: int
    :param no_defaults: return representations that do not include attributes with default values.
    :type no_defaults: bool

    :rtype: Report
    """
    logging.info(f"search_reports_by_report_id(): report_id={report_id}")
    report = next((report for report in reports if report.id == report_id), None)
    logging.debug(f"search_reports_by_report_id(): report={report}")
    return report

def update_report(report_id, body=None):  # noqa: E501
    """update a report

    Update the report specified by the reportID in path. # noqa: E501

    :param report_id: Numeric ID of a report.
    :type report_id: int
    :param body: Report item to update.
    :type body: dict | bytes

    :rtype: List[Report]
    """
    logging.info(f"update_report(): report_id={report_id}")
    reportBody = None
    if connexion.request.is_json:
        reportBody = Report.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_report(): reportBody={reportBody}")
    if reportBody is None:
        return []

    report = next((report for report in reports if report.id == report_id), None)
    if report is not None:
        reports.remove(report)

        # set modification date time
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        report.modification_date_time = current_time

        if reportBody.program_id != report.program_id:
            problem = Problem(title="Bad Request: program ID cannot be modified", status="400")
            logging.warning(f"update_report(): problem={problem}")
            return problem
        if reportBody.event_id is not None:
            report.event_id = reportBody.event_id
        if reportBody.client_id is not None:
            report.client_id = reportBody.client_id
        if reportBody.name is not None:
            report.name = reportBody.name
        if reportBody.name is not None:
            report.resources = reportBody.resources

        reports.append(report)
        logging.debug(f"update_report(): report={report}")

        for subscription in subscriptions:
            resource = next((resource for resource in subscription.resource_operations if
                             "REPORT" in resource.resources and "PUT" in resource.operations), None)
            if resource is not None:
                logging.debug(f"update_report(): resource={resource}")
                response = requests.post(resource.callback_url, json=json.dumps(report.to_dict()))
                if response.status_code != 200:
                    logging.warning(f"update_report: callback response.status_code={response.status_code}")

        return (report)

    return None
