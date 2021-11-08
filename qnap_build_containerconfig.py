import logging

class ContainerConfig(object):
    
    def __init__(self, c_name):
        self.c_name = c_name
    
    def tag(self, tag='latest'):
        self.c_tag = tag

    def container_image(self, container_image):
        container_image = container_image.split(':')
        self.c_config['image'] = container_image[0]
        if len(container_image) > 1:
            self.c_config['tag'] = container_image[1]

    def network_name(self, n_name, n_mode='dhcp', int_name='eth0'):
        net_data = {
            'mode': n_name,
            'bridge': {
                'mode':n_mode,
                'interface': {
                    'bridge': n_name,
                    'name': int_name
                }
            }
        }
        self.c_config['network'] = net_data
        return self.c_config['network']

    def run_command(self, command):
        self.c_config['command'] = command

    def host_volume(self, mount, bind, flag='ro'):
        try:
            if flag not in ['ro', 'rw']:
                raise Exception('Flag is not RO or RW')
        except:
            logging.error('Flag is not RO or RW, defaulting to RO (read-only)')
            flag = 'ro'
        vol_data = {
            mount: {
                'bind': bind,
                flag: True
            }
        }
        self.c_config['volume']['host'].update(vol_data)
        return self.c_config['volume']['host']

    def add_volume(self, v_dict):
        self.c_config['volume']['host'].update(v_dict)
        return self.c_config['volume']['host']

    def set_resource_limit(self, cputime=256, cpuweight=256, memory='1024m'):
        if (type(cputime) == int or type(cpuweight) == int) and type(memory) == str:
            if cputime >= 70 or cpuweight >= 70:
                logging.error('Configured CPU Time or Weight is over 75 percent')
                raise Exception('Over 75 precent threshold')
            self.c_config['resource']['limit']['cputime'] = cputime
            self.c_config['resource']['limit']['cpuweight'] = cpuweight
            self.c_config['resource']['limit']['memory'] = memory
        return self.c_config['resource']

    def environment(self, env_var):
        self.c_config['environment'].append(env_var)
        return self.c_config['environment']

    def entry_point(self, e_point):
        self.c_config = e_point
        return self.c_config['entrypoint']

    def autostart(self, a_start=True):
        self.c_config['autostart'] = a_start
        return self.c_config['autostart']

    def base_config(self):
        config = {
            'name': self.c_name,
            'type': 'docker',
            'image': '',
            'autostart': True,
            'entrypoint': '/init',
            'tag': '',
            'command': '',
            'environment': [],
            'volume': {
                'host': {}
            },
            'resource': {
                'limit': {
                    'cputime': 256,
                    'cpuweight': 256,
                    'memory': '1024m'
                }
            },
            'network': {}
        }
        self.c_config = config

    def get_config(self):
        return self.c_config