#!/usr/bin/env python
# This script fetches costs from CloudHealth

import os
import yaml
import json
import requests
import numpy as np

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
days = [day['name'] for day in res['dimensions'][0]['time']
        if day['name'] != 'total']
service_categories = [
    service['name'] for service in res['dimensions'][1]['AWS-Service-Category']
    if service['name'] != 'total']
costs_per_service = np.array(res['data'])
costs_per_service = costs_per_service[0]
costs_per_service.transpose()


data_per_service = {}
for service in service_categories:
    data_per_service[service] = []

for i in range(len(service_categories)):
    data_per_service[service_categories[i]] = list(
        zip(days, costs_per_service[i:]))

data_per_service['total'] = list(zip(days, costs_per_service[0:]))
pass
