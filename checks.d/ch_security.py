#!/usr/bin/env python
import os
import yaml
from checks import AgentCheck
from cloudhealth import client


filename = os.path.basename(__file__).split('.')
conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
with open(conf_path, 'r') as yaml_file:
    vars = yaml.load(yaml_file.read())
    api_key = vars.get('api_key')


def get_data():
    ch = client.CloudHealth(api_key['usr'])
    # ch = client.CloudHealth('28879f70-f4c5-0133-a747-22000b35812c')
    result = ch.assets.get('AwsSecurityGroupRule', 'security_group')
    unsafe_sg = []
    for rule in result:
        if rule['ip_ranges'] == "All" and rule['from_port'] == 0 and rule['to_port'] == 65535:
            unsafe_sg.append(rule['security_group']['group_id'].encode('ascii'))
    # print set(unsafe_sg)
    return len(set(unsafe_sg))


class ch_security(AgentCheck):
    def check(self, ch_security):
        task = get_data()
        self.gauge('unsafe_security_groups', task, tags=['unsafe-SG'])