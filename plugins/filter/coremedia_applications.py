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
