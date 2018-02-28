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

group_names = []
amounts = []
new_dict = {}

def get_data():
    key = api_key['usr']
    url = urls['cost_projects']
    all_data = requests.get(url+key)
    parsed = all_data.json()
    for key in parsed:
        if key == "dimensions":
            list =  parsed[key]
            new_list = list[0]
            final_list = new_list["Groupset-893353287079"]
            for i in final_list:
                for t in i:
                    if t == "label":
                        group_names.append(i[t])
        elif key == "data":
            amounts.append(parsed[key])
    dictionary = dict(zip(group_names, amounts[0]))
    for key, value in dictionary.items():
        if value[0]:
            value = float(value[0])
            new_dict[key] = value
    return new_dict

get_data()

class ch_projects(AgentCheck):
    def check(self, ch_projects):
        task = get_data()
        for key, value in task.items():
            self.gauge('Projects_Costs', value, tags=[key,'Project_Costs'])