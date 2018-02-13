#!/usr/bin/python
import os
from datetime import datetime

import yaml
from checks import AgentCheck
from keystoneauth1 import session
from keystoneauth1.identity import v2
from novaclient import client as novaclient
from keystoneclient.v3 import client as keystoneclient


def get_password_session(usernamme, password, url, project):
    auth = v2.Password(auth_url=url,
                       username=usernamme,
                       password=password,
                       tenant_name=project)
    return session.Session(auth=auth)


def get_created_time_time_format(created_time):
    created_time = (created_time).replace('T', ' ')
    created_time = created_time.replace('Z', '')
    created_time = \
        datetime.strptime(created_time,
                          '%Y-%m-%d %H:%M:%S')
    return created_time


def get_project_names(usernamme, password, url, project_name):
    password_session = get_password_session(usernamme=usernamme,
                                            password=password,
                                            url=url,
                                            project=project_name)
    keystone = keystoneclient.Client(session=password_session)

    projects_name = []
    projects_list = keystone.projects.list(user=password_session.get_user_id())

    for project in projects_list:
        projects_name.append(project.name.encode('ascii'))
    return projects_name


def set_global_var(config_file):
    with open(config_file) as config:
        conf_vars = yaml.load(config.read())
    OS_AUTH_URL = conf_vars['OS_AUTH_URL']
    OS_USERNAME = conf_vars['OS_USERNAME']
    OS_PASSWORD = conf_vars['OS_PASSWORD']
    flavor_count = conf_vars['flavors']
    metric_suffix = conf_vars['metric_suffix']
    project_name = conf_vars['project']
    global OS_AUTH_URL
    global OS_USERNAME
    global OS_PASSWORD
    global flavor_count
    global metric_suffix
    global project_name


def get_data(config_file):
    set_global_var(config_file)
    projects_names = get_project_names(OS_USERNAME, OS_PASSWORD, OS_AUTH_URL, project_name)
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

        if len(instances_list) > 0:
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


class OpenStack_Mon(AgentCheck):
    def check(self, *args):
        filename = os.path.basename(__file__).split('.')[0]
        config_file = '/etc/dd-agent/conf.d/{0}.yaml'.format(filename)
        flavor_count, tenants_instances = get_data(config_file)

        name = '{0}.instances'.format(metric_suffix)
        for flavor, num in flavor_count.items():
            tag = 'name:{0}'.format(flavor)

            self.gauge(name, num, tags=[tag])

        name = '{0}.tenants'.format(metric_suffix)
        for tenant, num in tenants_instances.items():
            tag = 'name:{0}'.format(tenant)
            self.gauge(name, num, tags=[tag])
