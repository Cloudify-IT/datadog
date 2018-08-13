#!/usr/bin/env python
# This script fetches costs from CloudHealth

import os
import yaml
import json
import requests

from checks import AgentCheck


def get_num_of_instances():
    filename = os.path.basename(__file__).split('.')
    conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
    with open(conf_path, 'r') as yaml_file:
        secrets = yaml.load(yaml_file)

    api_key = secrets['API_KEY']
    ch_report_id = secrets['CLOUDHEALTH_REPORT_ID']

    url = "https://chapi.cloudhealthtech.com/olap_reports/custom/" \
          "{0}?api_key={1}".format(ch_report_id, api_key)
    request = requests.get(url=url, headers={"Accept": "application/json"})
    res = json.loads(request.content)
    num_of_instances = -1
    for i in range(-1, -len(res['data']), -1):
        if res['data'][i][0] is not None:
            num_of_instances = res['data'][i][0]
            break
    return num_of_instances


class Check(AgentCheck):
    def check(self, *args):
        num_of_instances = get_num_of_instances()
        self.gauge('aws.num_of_ec2_instances', num_of_instances,
                   tags=['aws_num_of_ec2_instances'])
