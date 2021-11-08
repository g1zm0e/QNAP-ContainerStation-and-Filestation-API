import json
from qnap_containerstation import ContainerStation
from qnap_filestation import FileStation

def container_check(c_session, c_name):
    all_containers = c_session.list_container_names()
    exists = False
    if c_name in all_containers:
        exists = True
    return exists


qnap_host = '10.10.10.10' # blah.blah.com - Support for DNS 
username = 'username'
password = 'password'

fstation = FileStation(qnap_host, username, password) 
ctstation = ContainerStation(qnap_host, username, password)

container_info = ctstation.get_container('container_name')
container_exists = container_check(ctstation, 'container_name')

