#!/usr/bin/env python
# This script fetches costs from CloudHealth

import os
import yaml
import json
import requests
import numpy as np

from checks import AgentCheck


def fetch_report_data(ch_report_id, api_key):
    url = "https://chapi.cloudhealthtech.com/olap_reports/custom/" \
          "{0}?api_key={1}".format(ch_report_id, api_key)
    request = requests.get(url=url, headers={"Accept": "application/json"})
    return json.loads(request.content)


def get_costs():
    filename = os.path.basename(__file__).split('.')
    conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
    with open(conf_path, 'r') as yaml_file:
        secrets = yaml.load(yaml_file)

    api_key = secrets['API_KEY']
    ch_report_id = secrets['CLOUDHEALTH_REPORT_ID_COSTS']

    res = fetch_report_data(ch_report_id, api_key)

    service_categories = [service['name'] for service in
                          res['dimensions'][1]['AWS-Service-Category']]
    costs_per_service = np.array(res['data'])
    for i in range(-1, -len(costs_per_service), -1):
        if np.count_nonzero(costs_per_service[i] != None) > 0:
            costs_per_service = costs_per_service[i]
            break

    costs_per_service.transpose()

    # Each item in costs_per_service is a list with one value
    data_per_service = dict(zip(
        service_categories, (i[0] for i in costs_per_service)))

    keys = []
    for key, value in data_per_service.items():
        if value is None:
            keys.append(key)
    for key in keys:
        del data_per_service[key]

    return data_per_service


def get_costs_per_account():
    filename = os.path.basename(__file__).split('.')
    conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
    with open(conf_path, 'r') as yaml_file:
        secrets = yaml.load(yaml_file)

    api_key = secrets['API_KEY']
    ch_report_id = secrets['CLOUDHEALTH_REPORT_ID_COSTS_PER_ACCOUNT']

    res = fetch_report_data(ch_report_id, api_key)

    service_categories = [service['label'] for service in
                          res['dimensions'][1]['AWS-Account']]
    costs_per_account = np.array(res['data'])
    for i in range(-1, -len(costs_per_account), -1):
        if np.count_nonzero(costs_per_account[i] != None) > 0:
            costs_per_account = costs_per_account[i]
            break

    costs_per_account.transpose()

    # Each item in costs_per_service is a list with one value
    data_per_service = dict(zip(
        service_categories, (i[0] for i in costs_per_account)))

    keys = []
    for key, value in data_per_service.items():
        if value is None:
            keys.append(key)
    for key in keys:
        del data_per_service[key]

    return data_per_service


class Check(AgentCheck):
    def check(self, *args):
        data = get_costs()
        for service, cost in data.items():
            self.gauge('aws.{}'.format(service), cost, tags=['aws_costs'])
        data = get_costs_per_account()
        for account_label, cost in data.items():
            self.gauge('aws_costs_account.{}'.format(account_label),
                       cost, tags=['aws_costs_per_account'])
