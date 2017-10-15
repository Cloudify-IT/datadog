#!/usr/bin/env python
import os
import yaml
import requests
from checks import AgentCheck

filename = os.path.basename(__file__).split('.')
conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
with open(conf_path, 'r') as yaml_file:
    vars = yaml.load(yaml_file.read())
    api_key = vars.get('api_key')
    urls = vars.get('urls')

def get_data():
    key = api_key['usr']
    url = urls['usgae_instances']
    all_data = requests.get(url+key)
    parsed = all_data.json()
    for key in parsed:
        if key == "data":
            return parsed[key]

def clean_data():
    return (get_data()[-1])[0][0]

clean_data()

class ch_ins_num(AgentCheck):
    def check(self, ch_ins_num):
        task = clean_data()
        self.gauge('ch_ins_num', task, tags=['ins_num'])
