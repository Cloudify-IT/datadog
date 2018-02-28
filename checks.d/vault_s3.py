#!/usr/bin/env python
import yaml
import os
import boto3
from checks import AgentCheck

filename = os.path.basename(__file__).split('.')
conf_path = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename[0])
with open(conf_path, 'r') as yaml_file:
    vars = yaml.load(yaml_file.read())
    accounts = vars.get('accounts')

os.environ["AWS_ACCESS_KEY_ID"] = accounts['id']
os.environ["AWS_SECRET_ACCESS_KEY"] = accounts['secret']

def get_vault_s3_etag():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('gigavault')
    for obj in bucket.objects.all():
        if 'master' in (obj.key).lower():
            if (accounts['s3_etag']) in (obj.e_tag):
                return 1
            else:
                return 0

class vault_s3(AgentCheck):
    def check(self, etag):
        task = get_vault_s3_etag()
        self.gauge('vault_s3', task, tags=['vault_s3'])