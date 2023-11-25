#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os
import time
from docker.types import Mount
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.core.plugins.module_utils.directory import create_directory
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container
from ansible_collections.bodsch.coremedia.plugins.module_utils.properties import (write_properties_file, environments_from_file)

class CoremediaResetContentServer():
    """
    """
    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")
        self.content_server = module.params.get("content_server")
        self.content_server_ior = module.params.get("content_server_ior")
        self.coremedia_admin = module.params.get("coremedia_admin", {})
        self.cm_admin_username = self.coremedia_admin.get("username", "admin")
        self.cm_admin_password = self.coremedia_admin.get("password", "admin")
        self.management_container_image = module.params.get("management_container_image")
        self.environments_files = module.params.get("environments_files")
        self.extra_hosts = module.params.get("extra_hosts")
        self.sql_store = module.params.get("sql_store", {})

        self.sql_store_driver = self.sql_store.get("driver", None)
        self.sql_store_url = self.sql_store.get("url", None)
        self.sql_store_username = self.sql_store.get("username", None)
        self.sql_store_password = self.sql_store.get("password", None)

        self.properties_directory = f"{Path.home()}/.ansible/cache/coremedia/{self.content_server}"

    def run(self):
        """
        """
        _failed = True
        _changed = False
        _msg = "module init."

        create_directory(directory=self.properties_directory, owner="1000", group="1000", mode="0755")

        self.container = Container(self.module)

        images = self.container.container_images(self.management_container_image)

        # self.module.log(f"  - images : {images}")

        if images:
            """
            """
            output, status_code, status_msg = self.content_server_runlevel()
            # self.module.log(msg=f"  - runlevel online: {output}")

            if output:
                if self.module.check_mode:
                    _failed = False
                    _changed = False
                    _msg = f"we are in check mode, content-server {self.content_server} will not be reset."
                    self.module.log(_msg)
                else:
                    state, msg = self.container.container_stop(self.content_server)
                    self.module.log(msg=f"  - {state}, {msg}")
                    time.sleep(5)

                    content_server_reset = self.content_server_reset()
                    self.module.log(msg=f"  - reset: {content_server_reset}")
                    time.sleep(5)
                    _changed = True

                    state, msg = self.container.container_start(self.content_server)
                    self.module.log(msg=f"  - {state}, {msg}")
                    time.sleep(20)

                    output, status_code, status_msg = self.content_server_runlevel()
                    self.module.log(msg=f"  - runlevel online: {output}")

                    if status_code == 200:
                        _failed = False
                        _msg = f"Content server {self.content_server} successfully reset."

        else:
            _msg = f"Container Image {self.management_container_image} not found."

        return dict(
            failed=_failed,
            changed=_changed,
            msg=_msg
        )

    def content_server_runlevel(self):
        """
        :return:
        """
        cmd = []
        cmd.append("runlevel")
        cmd.append("--user")
        cmd.append(self.cm_admin_username)
        cmd.append("--password")
        cmd.append(self.cm_admin_password)
        if self.content_server_ior:
            cmd.append("--url")
            cmd.append(self.content_server_ior)

        _output, _status_code, _status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name=f"{self.content_server}-runlevel",
            cmd=cmd
        )

        online = len([match for match in _output if " run level is online" in match]) > 0

        self.module.log(msg=f"  - _output      : {_output}")
        self.module.log(msg=f"  - online       : {online}")
        self.module.log(msg=f"  - _status_code : {_status_code}")
        self.module.log(msg=f"  - _status_msg  : {_status_msg}")

        return online, _status_code, _status_msg

        # return self.container.run_container(cmd, env)

    def content_server_reset(self):
        """
        """
        env = None
        mounts = []

        if not self.environments_files:
            if self.sql_store_driver and self.sql_store_url and self.sql_store_username and self.sql_store_password:
                write_properties_file(self.module, os.path.join(self.properties_directory, "sql.properties"), self.sql_store)

                # mount points
                properties_dir = Mount(
                    target="/coremedia/tools/properties/corem/",
                    source=self.properties_directory,
                    type="bind"
                )

                mounts.append(properties_dir)

        if self.environments_files:
            env = environments_from_file(self.module, self.environments_files)

        cmd = []
        # cmd.append("tools/bin/cm")
        cmd.append("schemaaccess")
        cmd.append("dropAll")

        _output, _status_code, _status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name=f"{self.content_server}-reset",
            mounts=mounts,
            cmd=cmd,
            env=env
        )

        self.module.log(msg=f"  - _output      : {_output}")
        self.module.log(msg=f"  - _status_code : {_status_code}")
        self.module.log(msg=f"  - _status_msg  : {_status_msg}")

        # return self.container.run_container(cmd, env)

    def content_server_restart(self):
        """
        :return:
        """
        error, msg = self.container.container_restart(self.content_server)

        return error, msg


# ===========================================
# Module execution.


def main():
    """
    """
    args = dict(
        state=dict(
            default="runlevel",
            choices=["runlevel", "reset"]
        ),
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
        ),
        environments_files=dict(
            required=False,
            type="list"
        ),
        extra_hosts=dict(
            required=False,
            type="dict",
        ),
        sql_store=dict(
            required=False,
            type="dict",
        )
    )

    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=False,
    )

    p = CoremediaResetContentServer(module)
    result = p.run()

    module.log(f"= result: {result}")
    module.exit_json(**result)


if __name__ == '__main__':
    main()

"""
sql.store.driver       = org.postgresql.Driver
sql.store.url          = jdbc:postgresql://bce-cmpdb-sv04.tik.intern:5432/replication_live_server
sql.store.user         = replication_live_server
sql.store.password     = XXXX

CONTAINER="registry.cm.local/coremedia/management-tools:rc"

DOCKER_OPTS="--rm --network coremedia --entrypoint /coremedia/tools/bin/cm"
DOCKER_VOLUMES="
    --volume /opt/container/replication-live-server/sql.properties:/coremedia/tools/properties/corem/sql.properties:ro"

docker run \
  ${DOCKER_OPTS} \
  ${DOCKER_VOLUMES} \
  ${CONTAINER} \
    schemaaccess dropAll

docker restart replication-live-server
"""
