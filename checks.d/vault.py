#!/usr/bin/env python
import os
import yaml
import requests
from checks import AgentCheck


def check_vault(host, port, token, **kwargs):
    diff_content = '"vault-status":"up and running"'
    headers = {'X-Vault-Token': token}
    vault_url = 'http://{0}:{1}/v1/secret/health-check'.format(host, port)
    vault_get = requests.get(vault_url, headers=headers)
    vault_latency = vault_get.elapsed.microseconds / 1000
    if diff_content in vault_get.content:
        return 1, vault_latency
    else:
        return 0, vault_latency


class Vault(AgentCheck):
    def check(self, instances, **kwargs):
        filename = os.path.basename(__file__).split('.')
        filename = filename[0]
        conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename)
        with open(conf_path, 'r') as yaml_file:
            vars = yaml.load(yaml_file.read())
            instances = vars.get('instances')
        for instance in instances:
            name = instance['name']
            host = instance['host']
            port = instance['port']
            token = instance['token']
            task, latency = check_vault(host, port, token)
            self.gauge(name, task, tags=['vault', name])
            self.gauge('{0}_latency'.format(name), latency, tags=['{0}_latency'.format(name)])
