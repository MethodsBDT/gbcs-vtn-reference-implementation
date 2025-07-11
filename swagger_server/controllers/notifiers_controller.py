import connexion
import six

from swagger_server.models.notifiers_response import NotifiersResponse  # noqa: E501
from swagger_server import util


def list_all_notifiers():  # noqa: E501
    """List all notifier bindings

    List all notifier bindings supported by the server  # noqa: E501


    :rtype: NotifiersResponse
    """
    return 'do some magic!'
