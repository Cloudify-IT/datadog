#!/usr/bin/python
import os
from subprocess import check_output

import yaml
import json

from checks import AgentCheck


def get_project_list():
    output = check_output(
        ["openstack", "project", "list", "--long", "--format=json"])
    projects = json.loads(output)
    return filter(lambda project: 'ID' in project and 'Name' in project,
                  projects)


def list_servers(project_name):
    os.environ['OS_PROJECT_NAME'] = project_name
    output = check_output(
        ["openstack", "server", "list", "--long", "--format=json"])
    servers = json.loads(output)
    return filter(lambda server: 'Status' in server
                                 and server['Status'] == 'ACTIVE'
                                 and 'Name' in server, servers)


def set_environ_vars(config_file):
    with open(config_file) as config:
        conf_vars = yaml.load(config.read())
    for key, value in conf_vars['ENV_VARS'].items():
        os.environ[key] = value
    flavor_count = conf_vars['flavors']
    metric_suffix = conf_vars['metric_suffix']
    global flavor_count
    global metric_suffix


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


class OpenStack_Mon(AgentCheck):
    def check(self, *args):
        filename = os.path.basename(__file__).split('.')[0]
        config_file = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename)
        flavor_count, tenants_instances = get_data(config_file)

        name = '{0}.instances'.format(metric_suffix)
        for flavor, num in flavor_count.items():
            tag = 'name:{0}'.format(flavor)

            self.gauge(name, num, tags=[tag])

        project_name_dict = {
            'tenant_name': 'tenant custom name'
        }
        name = '{0}.tenants'.format(metric_suffix)
        for tenant, num in tenants_instances.items():
            if tenant in project_name_dict:
                tag = 'name:{0}_{1}'.format(tenant, project_name_dict[tenant])
            else:
                tag = 'name:{0}'.format(tenant)
            self.gauge(name, num, tags=[tag])
