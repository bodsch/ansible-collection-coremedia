#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container
from ansible_collections.bodsch.coremedia.plugins.module_utils.coremedia import Coremedia


class CoremediaContentServerOnline():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")
        self.management_container_image = module.params.get("management_container_image")
        self.content_server = module.params.get("content_server")
        self.content_server_ior = module.params.get("content_server_ior")
        self.coremedia_admin = module.params.get("coremedia_admin", {})
        self.cm_admin_username = self.coremedia_admin.get("username", "admin")
        self.cm_admin_password = self.coremedia_admin.get("password", "admin")

    def run(self):
        """
        """
        self.container = Container(self.module)

        management_container_image = self.container.container_images(image_name=self.management_container_image)

        if not management_container_image:

            return dict(
                failed=True,
                changed=False,
                msg=f"Container Image {self.management_container_image} not found."
            )

        container = self.container.container_search(self.content_server)

        if container:
            self.content_server = container.get("Name", '')[1:]   # cut first char

        if self.content_server:
            """
            """
            online, output, status_code, status_msg = self.content_server_runlevel()

            self.module.log(msg=f"  - runlevel online: {online}, {output}")

            return dict(
                failed=False,
                changed=False,
                online=online,
                msg=output[0]
            )

        return dict(
            failed=True,
            changed=False,
            msg="Module default result."
        )

    def content_server_runlevel(self):
        """
        :return:
        """
        self.coremedia = Coremedia(self.module)

        online, output, status_code, status_msg = self.coremedia.content_server_runlevel(
            self.management_container_image,
            self.content_server,
            self.cm_admin_username,
            self.cm_admin_password,
            self.content_server_ior)

        return (online, output, status_code, status_msg)


def main():
    """
    """
    args = dict(
        management_container_image=dict(
            required=True,
            type="str"
        ),
        content_server=dict(
            required=True,
            choices=["replication-live-server", "master-live-server", "content-management-server"],
            type="str"
        ),
        content_server_ior=dict(
            required=True,
            type="str"
        ),
        coremedia_admin=dict(
            required=False,
            type="dict",
        )
    )

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=False,
    )

    p = CoremediaContentServerOnline(module)
    result = p.run()

    module.log(f"= result: {result}")
    module.exit_json(**result)


if __name__ == '__main__':
    main()
