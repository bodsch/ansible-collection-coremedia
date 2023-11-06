#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os
import shutil
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container
from ansible_collections.bodsch.core.plugins.module_utils.checksum import Checksum
from ansible_collections.bodsch.core.plugins.module_utils.directory import create_directory
from docker.types import Mount
from pathlib import Path


class CoremediaFeeder():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")
        self.container_image = module.params.get("container_image")
        self.data_directory = module.params.get("data_directory")
        self.cms_ior = module.params.get("cms_ior")
        self.cms_username = module.params.get("cms_username")
        self.cms_password = module.params.get("cms_password")
        self.mls_ior = module.params.get("mls_ior")

        self.checksum_directory = f"{Path.home()}/.ansible/cache/coremedia/import_users"

    def run(self):
        """
        """
        if not self.container_image:
            return dict(
                failed=True,
                msg="No Container Image defined."
            )

        self.checksum = Checksum(self.module)
        create_directory(directory=self.checksum_directory, mode="0750")

        old_checksum = None
        new_checksum = None

        old_filename = os.path.join(self.checksum_directory, "users.xml")
        new_filename = os.path.join(self.data_directory, "users.xml")

        if os.path.isfile(old_filename):
            old_checksum = self.checksum.checksum_from_file(old_filename)

        if os.path.isfile(new_filename):
            new_checksum = self.checksum.checksum_from_file(new_filename)

        changed = not (new_checksum == old_checksum)
        # new_file = False
        msg = "The users.xml has not been changed"

        self.module.log(msg=f" - old_filename {old_filename}  {old_checksum}")
        self.module.log(msg=f" - new_filename {new_filename}  {new_checksum}")
        self.module.log(msg=f" - changed {changed}")
        # self.module.log(msg=f" - vhost {vhost}")

        if changed:
            self.container = Container(self.module)

            images = self.container.container_images(self.container_image)

            if images and isinstance(images, dict):
                """
                """
                self.module.log(msg=f" - images : {images}")

                res = {}

                _failed = True
                _changed = False

                status_code, status_msg, msg = self.import_users()
                self.module.log(msg=f" status_code: {status_code}")
                self.module.log(msg=f" status_msg : {status_msg}")
                self.module.log(msg=f" msg        : {msg}")

                res.update({"restore user": msg})

                if int(status_code) == 200:
                    _failed = False
                    _changed = True
                else:
                    _failed = True

                shutil.copy(new_filename, old_filename)

                return dict(
                    failed=_failed,
                    changed=_changed,
                    msg=res
                )

            else:
                return dict(
                    failed=True,
                    changed=False,
                    msg=f"Missing container: {self.container_image}"
                )

        else:
            return dict(
                failed=False,
                changed=False,
                msg=msg
            )

    def import_users(self):

        env = dict(
            CMS_IOR_URL=self.cms_ior,
            MLS_IOR_URL=self.mls_ior
        )

        cmd = [
            "restoreusers",
            "--user", self.cms_username,
            "--password", self.cms_password,
            "--url", self.cms_ior,
            "--file",
            os.path.join("/run/host", "users.xml"),
        ]

        # mount points
        user_dir = Mount(
            target="/run/host",
            source=self.data_directory,
            type="bind"
        )

        mounts = []
        mounts.append(user_dir)

        _output, _status_code, _status_msg = self.container.run_container(
            container_image=self.container_image,
            name="restoreusers",
            mounts=mounts,
            cmd=cmd,
            env=env
        )

        msg = self._parse_container_output(_output)

        return _status_code, _status_msg, msg

    def _parse_container_output(self, output):
        """
            Import /run/host/users.xml ...
            Done.
        """
        result = []

        pos = [
            "Import",
            "Done",
        ]

        for line in output:
            if line.startswith(tuple(pos)):
                result.append(line)

        return result


def main():
    """
    :return:
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                default="import",
                choices=["import", "publish"]
            ),
            container_image=dict(
                required=True,
                type="str"
            ),
            data_directory=dict(
                required=True,
                type="str"
            ),
            cms_username=dict(
                required=False,
                type="str"
            ),
            cms_password=dict(
                required=False,
                type="str",
                no_log=True
            ),
            cms_ior=dict(
                required=False,
                type="str"
            ),
            mls_ior=dict(
                required=False,
                type="str"
            )
        ),
        supports_check_mode=True,
    )

    p = CoremediaFeeder(module)
    result = p.run()

    module.log(msg="= result: {}".format(result))
    module.exit_json(**result)


if __name__ == '__main__':
    main()

# {{ cms_tools_dir }}/bin/cm restoreusers --user admin --password admin --file {{ item }}
