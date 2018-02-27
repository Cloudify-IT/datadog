#!/usr/bin/python
import os
import urllib2

import yaml
import json

# from checks import AgentCheck
from keystoneauth1 import session
from keystoneauth1.identity import v3
from novaclient import client as novaclient


class InvalidResponse(Exception):
    pass


def get_password_session(usernamme, password, url, project):
    auth = v3.Password(auth_url=url,
                       username=usernamme,
                       password=password,
                       user_domain_name='Default',
                       project_name=project,
                       project_domain_name='Default')
    return session.Session(auth=auth)


def get_response(method_name, **kwargs):
    url = "https://api.memset.com/v1/json/{0}?".format(method_name)
    for key, value in kwargs.items():
        url += "{0}={1}&".format(key, value)
    response = json.loads(urllib2.urlopen(url).read())
    if 'error_code' in response and response['error_code']:
        raise response
    return InvalidResponse(str(response))


def get_project_list(api_key):
    projects = get_response(method_name='openstack.list_projects', api_key=api_key)
    return [projects[key]['project_id'] for key in projects.keys() if 'project_id' in projects[key]]


def list_servers(api_key):
    servers = get_response(method_name='server.list', api_key=api_key)
    return []


def set_global_var(config_file):
    with open(config_file) as config:
        conf_vars = yaml.load(config.read())
    OS_AUTH_URL = conf_vars['OS_AUTH_URL']
    OS_USERNAME = conf_vars['OS_USERNAME']
    OS_PASSWORD = conf_vars['OS_PASSWORD']
    API_KEY = conf_vars['API_KEY']
    flavor_count = conf_vars['flavors']
    metric_suffix = conf_vars['metric_suffix']
    project_name = conf_vars['project']
    global OS_AUTH_URL
    global OS_USERNAME
    global OS_PASSWORD
    global API_KEY
    global flavor_count
    global metric_suffix
    global project_name


def get_data(config_file):
    set_global_var(config_file)
    projects_names = get_project_list(api_key=API_KEY)
    tenants_instances = {}
    total_instances = 0
    for project in projects_names:
        instances_count = 0
        password_session = get_password_session(OS_USERNAME, OS_PASSWORD,
                                                OS_AUTH_URL, project)
        nova = novaclient.Client(version='2.0', session=password_session)
        instances_list = nova.servers.list()
        total_instances += 0
        tenants_instances[project] = 0

        for instance in instances_list:
            if 'ACTIVE' in instance.status:
                total_instances += 1
                tenants_instances[project] += 1
                instances_count += 1
                flavor = \
                    nova.flavors.get(instance.flavor['id']).name.encode('ascii')
                try:
                    flavor_count[flavor] += 1
                except KeyError:
                    flavor_count[flavor] = 1
    tenants_instances['Total'] = total_instances
    return flavor_count, tenants_instances


filename = os.path.basename(__file__).split('.')[0]
config_file = 'Memset.test.yaml'.format(filename)
flavor_count, tenants_instances = get_data(config_file)
print()

# class OpenStack_Mon(AgentCheck):
#     def check(self, *args):
#         filename = os.path.basename(__file__).split('.')[0]
#         config_file = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename)
#         flavor_count, tenants_instances = get_data(config_file)
#
#         name = '{0}.instances'.format(metric_suffix)
#         for flavor, num in flavor_count.items():
#             tag = 'name:{0}'.format(flavor)
#
#             self.gauge(name, num, tags=[tag])
#
#         name = '{0}.tenants'.format(metric_suffix)
#         for tenant, num in tenants_instances.items():
#             tag = 'name:{0}'.format(tenant)
#             self.gauge(name, num, tags=[tag])
