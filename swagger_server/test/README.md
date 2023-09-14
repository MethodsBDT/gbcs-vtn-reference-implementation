# tests for RI

These are just simple 'smoke' tests for the RI

## create a virtual environment and run pytests 
from RI-3.0.0 folder
$ virtualenv venv
$ source venv/bin/activate
(venv)$ pip3 install -r requirements.txt
(venv)$ pip3 install -r test-requirements.txt
(venv)$ cd swagger_server
(venv)swagger_server$ pytest