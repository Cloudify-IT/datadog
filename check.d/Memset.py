#!/usr/bin/python
import os
import subprocess

import yaml
import json


# from checks import AgentCheck

class InvalidResponse(Exception):
    pass


def get_project_list():
    output = subprocess.check_output("openstack project list --long --format=json")
    projects = json.loads(output)
    return filter(lambda project: 'ID' in project and 'Name' in project, projects)


def list_servers(project_name):
    os.environ['OS_PROJECT_NAME'] = project_name
    server_list_shell = subprocess.Popen(["openstack", "server", "list", "--long", ",--format=value"],
                                         stdout=subprocess.PIPE)
    grep_server_list_shell = subprocess.Popen(["grep", "-v", "SHELVED_OFFLOADED"],
                                              stdin=server_list_shell.stdout)
    server_list_shell.stdout.close()
    output, err = grep_server_list_shell.communicate()
    if err:
        raise InvalidResponse(str(err))
    servers = json.loads(output)
    return filter(lambda server: 'Status' in server and server['Status'] == 'ACTIVE' and 'Name' in server,
                  servers)


def set_environ_vars(config_file):
    with open(config_file) as config:
        conf_vars = yaml.load(config.read())
    os.environ['OS_AUTH_URL'] = conf_vars['OS_AUTH_URL']
    os.environ['OS_USERNAME'] = conf_vars['OS_USERNAME']
    os.environ['OS_PASSWORD'] = conf_vars['OS_PASSWORD']
    os.environ['OS_USER_DOMAIN_NAME'] = conf_vars['OS_USER_DOMAIN_NAME']
    os.environ['OS_REGION_NAME'] = conf_vars['OS_REGION_NAME']
    flavor_count = conf_vars['flavors']
    metric_suffix = conf_vars['metric_suffix']
    project_name = conf_vars['project']
    global flavor_count
    global metric_suffix
    global project_name


def get_data(config_file):
    set_environ_vars(config_file)
    projects_names = get_project_list()
    tenants_instances = {}
    total_instances = 0
    for project in projects_names:
        instances_count = 0
        instances = list_servers(project['Name'])
        total_instances += 0
        tenants_instances[project['Name']] = 0

        for instance in instances:
            if 'ACTIVE' == instance['Status']:
                total_instances += 1
                tenants_instances[project['Name']] += 1
                instances_count += 1
                flavor = instance['Flavor Name']
                if flavor in flavor_count:
                    flavor_count[flavor] += 1
                else:
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
