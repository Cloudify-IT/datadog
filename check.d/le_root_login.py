#!/usr/bin/env python
import re
import os
import yaml
import requests
import json
import time
import datetime
from checks import AgentCheck

filename = os.path.basename(__file__).split('.')
conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
with open(conf_path, 'r') as yaml_file:
    vars = yaml.load(yaml_file.read())
    api_key = vars.get('api_key')
    urls = vars.get('urls')

def continue_request(req):
    if 'links' in req.json():
        continue_url = req.json()['links'][0]['href']
        new_response = make_request(continue_url)
        return handle_response(new_response)


def handle_response(resp):
    response = resp
    time.sleep(5)
    if response.status_code == 200:
        for match in re.finditer('global_timeseries":{"count":(.*?).0}', resp.content, re.S):
            return  match.group(1)
    if response.status_code == 202:
        return continue_request(resp)
    if response.status_code > 202:
        print 'Error status code ' + str(response.status_code)
        return

def make_request(provided_url=None):
    day_before_yesterday = datetime.date.today() - datetime.timedelta(2)
    unix_time = str(day_before_yesterday.strftime("%s")) + "000"
    now = str(int(time.time())) + "000"
    headers = {'x-api-key': api_key['usr']}
    payload = {'query': 'where(/[0-9]{1,9}:root/ AND ConsoleLogin) calculate(count)', 'from': unix_time, 'to': now}
    url = urls['lambda_events']
    if provided_url:
        url = provided_url
    req = requests.get(url, headers=headers, params=payload)
    return req


def print_query():
    req = make_request()
    return handle_response(req)

def start():
    return print_query()

class le_root_login(AgentCheck):
    def check(self, le_root):
        task = start()
        self.gauge("root account access-", task, tags=["root_login_to_console"])