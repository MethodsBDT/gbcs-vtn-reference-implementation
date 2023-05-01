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
    description="OpenADR REST Demand Response API",
    author_email="frank@pajaritotech.com",
    url="",
    keywords=["Swagger", "OpenADR REST Demand Response API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    The OpenADR REST API supports energy retailer to energy customer Demand Response programs. The API includes the following capabilities and operations:  __Manage programs:__  * Create/Update/Delete a program * Search programs  __Manage events:__  * Create/Update/Delete an event * Search events  __Manage reports:__  * Create/Update/Delete a report * Search reports  __Manage subscriptions:__  * Create/Update/Delete subscriptions to programs, events, and reports * Search subscriptions * Subscriptions allows clients to register a callback URL (webhook) to be notified   on the change of state of a resource  __Manage vens:__  * Create/Update/Delete vens and ven resources * Search ven and ven resources  __Manage tokens:__  * Obtain an access token * This endpoint is provided as a convenience and may be neglected in a commercial implementation 
    """
)
