#!/usr/bin/env python
# This script fetches costs from CloudHealth

import os
import yaml
import json
import requests
import numpy as np

from checks import AgentCheck


def get_data():
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
    service_categories = [service['name'] for service in
                          res['dimensions'][1]['AWS-Service-Category']]
    costs_per_service = np.array(res['data'])
    costs_per_service = costs_per_service[-1]
    costs_per_service.transpose()

    # Each item in costs_per_service is a list with one value
    data_per_service = dict(zip(
        service_categories, (i[0] for i in costs_per_service)))

    return data_per_service


class Check(AgentCheck):
    def check(self, *args):
        data = get_data()
        for service, cost in data.items():
            self.gauge('aws.{}'.format(service), cost, tags=['aws_costs'])
