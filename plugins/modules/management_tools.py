#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.coremedia import Coremedia


class CoreMediaManagementTools:
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.management_container_image = module.params.get("management_container_image")

    def run(self):
        """
        """
        self.coremedia = Coremedia(self.module)

        _container_status = self.coremedia.management_tools(self.management_container_image)

        result = dict()
        result.update(_container_status)

        return result


def main():

    module = AnsibleModule(
        argument_spec=dict(
            management_container_image=dict(
                required=True,
                type="str"
            )
        ),
        supports_check_mode=True,
    )

    p = CoreMediaManagementTools(module)
    result = p.run()

    module.log(msg="= result: {}".format(result))
    module.exit_json(**result)


if __name__ == '__main__':
    main()
