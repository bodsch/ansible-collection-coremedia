# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    """

    def filters(self):
        return {
            'coremedia_applications': self.coremedia_applications,
            'coremedia_container': self.coremedia_container,
        }

    def coremedia_applications(self, data):
        """
        :param data:
        :return:
        """
        result = []

        result = list(data.keys())

        display.v(f" = result {result} {type(result)}")

        return result

    def coremedia_container(self, data, container):
        """
        :param data:
        :return:
        """
        # display.v(f"coremedia_applications(self, {data}, {container})")
        result = []
        result = len([x for x in data if x.get("name") == container]) != 0

        display.v(f" = result {container}: {result} {type(result)}")
        return result
