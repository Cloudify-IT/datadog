
import subprocess
# from checks import AgentCheck


def find_string_between_strings(string, first, last):
    try:
        start = string.index(first) + len(first)
        end = string.index(last, start)
        return string[start:end]
    except ValueError:
        return ' '


def get_offest_in_second():
    offset = subprocess.check_output(
        'sudo service datadog-agent info | grep "Status date:"', shell=True)
    offset = offset.splitlines()
    offset = find_string_between_strings(offset[0], '(', ' s ago)')
    return offset

print get_offest_in_second()

# class Ntp_Offest(AgentCheck):
#     def check(self, **kwargs):
#         offset = get_offest_in_second()
#         self.gauge('NTP_offset', offset, tags=['NTP_offset'])