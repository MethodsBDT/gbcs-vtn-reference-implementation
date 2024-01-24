import connexion
from datetime import datetime
from http import HTTPStatus
import logging

from swagger_server.models.object_id import ObjectID  # noqa: E501
from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.report import Report  # noqa: E501
from swagger_server.controllers.subscriptions_controller import subscription_callback  # noqa: E501
from swagger_server.objStore.storageInterface import objStore

def create_report(body=None):  # noqa: E501
    """add a report

    Create a new report in the server. # noqa: E501

    :param body: report item to add.
    :type body: dict | bytes

    :rtype: Report
    """
    logging.info(f"create_report():")

    reportBody = None
    if connexion.request.is_json:
        reportBody = Report.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"create_report(): reportBody={reportBody}")
    # if reportBody is None:
    #     problem = Problem(title="Bad Request: No request body", status="400")
    #     logging.warning(f"create_report(): problem={problem}")
    #     return problem, 400
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    report = Report(
        created_date_time=current_time,
        modification_date_time=None,
        object_type='REPORT',
        program_id=reportBody.program_id,
        event_id=reportBody.event_id,
        client_name=reportBody.client_name,
        report_name=reportBody.report_name,
        payload_descriptors=reportBody.payload_descriptors,
        resources=reportBody.resources
    )

    status = objStore.insert(report)
    if status != HTTPStatus.CREATED:
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"create_report(): problem={problem}")
        return problem, status
    logging.debug(f"create_report(): report={report}")

    subscription_callback("REPORT", "POST", report)

    return report, status

def delete_report(report_id):  # noqa: E501
    """delete a report

    Delete the repoprt specified by the reportID in path. # noqa: E501

    :param report_id: object ID of a report.
    :type report_id: dict | bytes

    :rtype: Report
    """
    report = objStore.remove("REPORT", report_id)
    if type(report) is not Report:
        status = report
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"delete_report(): problem={problem}")
        return problem, status

    # TBD: need to test if this is not present
    subscription_callback("REPORT", "DELETE", report)

    return report, HTTPStatus.OK


def search_all_reports(program_id=None, event_id=None, client_name=None, skip=None, limit=None):  # noqa: E501
    """searches all reports

    List all reports known to the server. May filter results by programID and clientName as query param. Use skip and pagination query params to limit response size.  # noqa: E501

    :param program_id: filter results to reports with programID.
    :type program_id: dict | bytes
    :param event_id: filter results to reports with eventID.
    :type event_id: dict | bytes
    :param client_name: filter results to reports with clientName.
    :type client_name: str
    :param skip: number of records to skip for pagination.
    :type skip: int
    :param limit: maximum number of records to return.
    :type limit: int

    :rtype: List[Report]
    """
    logging.info(f"search_all_reports(): program_id={program_id} client_name={client_name} skip={skip} limit={limit}")

    reports = objStore.search_all("REPORT")
    if type(reports) is not list:
        status = reports
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_all_reports(): problem={problem}")
        return problem, status

    if program_id != None:
        reports = [report for report in reports if report.program_id == program_id]
        if len(reports) == 0:
            return reports, HTTPStatus.OK
    if event_id != None:
        reports = [report for report in reports if report.event_id == event_id]
        if len(reports) == 0:
            return reports, HTTPStatus.OK
    if client_name != None:
        reports = [report for report in reports if report.client_name == client_name]
        if len(reports) == 0:
            return reports, HTTPStatus.OK
    if skip != None:
        if len(reports) < skip:
            problem = Problem(title="Not Found: skipped records not found", status="404")
            logging.warning(f"search_all_reports(): problem={problem}")
            return problem, HTTPStatus.NOT_FOUND
        reports = reports[skip:]
    if limit != None:
        reports = reports[:limit]

    logging.debug(f"search_all_reports(): reports={reports}")

    subscription_callback("REPORT", "GET", reports)

    return reports, HTTPStatus.OK


def search_reports_by_report_id(report_id):  # noqa: E501
    """searches reports by reportID

    Fetch the report specified by the reportID in path. # noqa: E501

    :param report_id: object ID of a report.
    :type report_id: dict | bytes

    :rtype: Report
    """
    logging.info(f"search_reports_by_report_id(): report_id={report_id}")
    report = objStore.search("REPORT", report_id)
    if type(report) is not Report:
        status = report
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"search_reports_by_report_id(): problem={problem}")
        return problem, status

    logging.debug(f"search_reports_by_report_id(): report={report}")

    subscription_callback("REPORT", "GET", report)

    return report, HTTPStatus.OK

def update_report(report_id, body=None):  # noqa: E501
    """update a report

    Update the report specified by the reportID in path. # noqa: E501

    :param report_id: object ID of a report.
    :type report_id: dict | bytes
    :param body: Report item to update.
    :type body: dict | bytes

    :rtype: Report
    """
    logging.info(f"update_report(): report_id={report_id}")
    reportBody = None
    if connexion.request.is_json:
        reportBody = Report.from_dict(connexion.request.get_json())  # noqa: E501
        logging.debug(f"update_report(): reportBody={reportBody}")
    # if reportBody is None:
    #     problem = Problem(title="Bad Request: No request body", status="400")
    #     logging.warning(f"update_ven(): problem={problem}")
    #     return problem, 400
    
    report, status = search_reports_by_report_id(report_id)
    if report is None or status == HTTPStatus.NOT_FOUND:
        problem = Problem(title="Not Found: report_id not found", status="404")
        logging.warning(f"update_report(): problem={problem}")
        return problem, HTTPStatus.NOT_FOUND

    # set modification date time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    report.modification_date_time = current_time

    if reportBody.program_id != report.program_id:
        problem = Problem(title="Bad Request: program ID cannot be modified", status="400")
        logging.warning(f"update_report(): problem={problem}")
        return problem, HTTPStatus.BAD_REQUEST
    if reportBody.event_id is not None:
        report.event_id = reportBody.event_id
    if reportBody.client_name is not None:
        report.client_name = reportBody.client_name
    if reportBody.report_name is not None:
        report.report_name = reportBody.report_name
    if reportBody.resources is not None:
        report.resources = reportBody.resources

    report = objStore.update("REPORT", report)
    if type(report) is not Report:
        status = report
        problem = Problem(title="object Storage issue", status=str(status))
        logging.warning(f"update_report(): problem={problem}")
        return problem, status

    logging.debug(f"update_report: report={report}")

    subscription_callback("REPORT", "PUT", report)

    return report, HTTPStatus.OK

