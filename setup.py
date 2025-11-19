# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="OpenADR 3 API",
    author_email="frank@pajaritotech.com",
    url="",
    keywords=["Swagger", "OpenADR 3 API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    The OpenADR 3 API supports energy retailer to energy customer Demand Response programs. See OpenADR 3 User Guide and Definitions for detailed descriptions of usage. The API includes the following capabilities and operations:  __Manage programs:__  * Create/Update/Delete a program * Search programs  __Manage events:__  * Create/Update/Delete an event * Search events  __Manage reports:__  * Create/Update/Delete a report * Search reports  __Manage subscriptions:__  * Create/Update/Delete subscriptions to programs, events, and reports * Search subscriptions * Subscriptions allows clients to register a callback URL (webhook) to be notified   on the change of state of a resource  __Manage vens:__  * Create/Update/Delete vens and ven resources * Search ven and ven resources  __List notifiers:__  * List all notification protocols, and for each notifier, usage details  __List MQTT notifier object topic names:__  * List all MQTT broker topic names for an object and the operations upon the object  __Manage tokens:__  * Obtain an access token * This endpoint is provided as a convenience and may be neglected in a commercial implementation
    """
)
