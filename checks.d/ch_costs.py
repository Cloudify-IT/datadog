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
    urls = vars.get('urls')


def get_data():
    ch = client.CloudHealth(api_key['usr'])
    return ch.cost.get_cost_for_instances()[utils._get_yesterdays_date()]

class ch_costs(AgentCheck):
    def check(self, ch_costs):
        task = get_data()
        self.gauge('ch_costs', task, tags=['costs'])