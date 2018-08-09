#!/usr/bin/env python
# This script fetches costs from CloudHealth

import os
import yaml
import requests

filename = os.path.basename(__file__).split('.')
conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
with open(conf_path, 'r') as yaml_file:
    secrets = yaml.load(yaml_file)

api_key = secrets['API_KEY']
ch_report_id = secrets['CLOUDHEALTH_REPORT_ID']

url = "https://chapi.cloudhealthtech.com/olap_reports/custom/" \
      "{0}?api_key={1}".format(ch_report_id, api_key)
request = requests.get(url=url, headers={"Accept": "application/json"})
pass
