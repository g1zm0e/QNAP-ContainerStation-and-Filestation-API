import json
import logging
from qnap import Qnap

class ContainerStation(Qnap):

    def list_container_names(self):
        return [x['name'] for x in self.list_containers()]
    
    def list_network_names(self):
        return [x['Name'] for x in self.list_networks()]

    def list_containers(self):
        return self.get(self.ctstation_endpoint('/container'))
    
    def list_networks(self):
        return self.get(self.ctstation_endpoint('/networks'))
    
    def get_container(self, c_name):
        return self.get(self.ctstation_endpoint(f'/container/{c_name}'))
    
    def inspect_container(self, c_name, c_type='docker'):
        return self.get(self.ctstation_endpoint(f'/container/{c_type}/{c_name}/inspect'))

    def delete_container(self, c_id, c_type='docker'):
        return self.delete(self.ctstation_endpoint(f'/container/{c_type}/{c_id}'))
    
    def stop_container(self, c_id, c_type='docker'):
        return self.put(self.ctstation_endpoint(f'/container/{c_type}/{c_id}/stop'))

    def build_container(self, config):
        try:
            self.build_config = json.dumps(config)
            return self.post(self.ctstation_endpoint('/container'), self.build_config)
        except:
            logging.error('Config is not JSON')