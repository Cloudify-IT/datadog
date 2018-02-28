#!/usr/bin/env python

import urllib
import re
from checks import AgentCheck


def get_external_ip():
    site = urllib.urlopen("http://checkip.dyndns.org/").read()
    grab = re.findall('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', site)
    address = grab[0]
    if '213.57.84.202' in address:
        return 1
    else:
        return 0


class Myip(AgentCheck):
    def check(self, ip):
        task = get_external_ip()
        self.gauge('my_ip', task, tags=['my_ip'])

