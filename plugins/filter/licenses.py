# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.display import Display

import sys

display = Display()

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class FilterModule(object):
    """
    """

    def filters(self):
        return {
            "validate_license_informations": self.validate_licenses,
        }

    def validate_licenses(self, data):
        """
        """
        display.v(f"validate_licenses({data})")

        if isinstance(data, list):
            lic = [x for x in data if x.get("service", None) and x.get("file", None)]
            # display.v(f"- {len(lic)}")

            if len(lic) != 0:
                return True
        else:
            return False
