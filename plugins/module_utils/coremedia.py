#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container


class Coremedia():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        # self.module.log("Coremedia::__init__")

        self.container = Container(self.module)

    def container_running(self, container, args):
        """
        """
        pass

    def content_server_runlevel(self, management_container_image, content_server, admin_username, admin_password, ior):
        """
            :return:
        """
        cmd = []
        cmd.append("runlevel")
        cmd.append("--user")
        cmd.append(admin_username)
        cmd.append("--password")
        cmd.append(admin_password)
        if ior:
            cmd.append("--url")
            cmd.append(ior)

        output, status_code, status_msg = self.container.run_container(
            container_image=management_container_image,
            name=f"{content_server}-runlevel",
            cmd=cmd,
        )

        online = len([match for match in output if " run level is online" in match]) > 0

        # self.module.log(msg=f"  - online      : {online}")
        # self.module.log(msg=f"  - output      : {output}")
        # self.module.log(msg=f"  - status_code : {status_code}")
        # self.module.log(msg=f"  - status_msg  : {status_msg}")

        return online, output, status_code, status_msg

    def feeder_status(self, feeder_name):
        """
        :return:
        """
        result = dict(
            status="unknown",
            running=False
        )

        container = self.container.container_search(feeder_name)

        if container and isinstance(container, dict):
            """
            """
            container_state = container.get('State', {})
            _status = container_state.get("Status", None)
            _running = container_state.get("Running", False)

            self.module.log(msg=f"  - status : {_status}")
            self.module.log(msg=f"  - running: {_running}")

            result = dict(
                feeder=feeder_name,
                status=_status,
                running=_running
            )

        return result

    def management_tools(self, management_container_image):
        """
        """
        result = dict(
            failed=False,
            exists=False,
            msg=f"Image {management_container_image} not found."
        )

        images = self.container.container_images(management_container_image)
        self.module.log(f"  - images : {images}")

        if images and isinstance(images, dict):
            _image_name = list(images.keys())[0]

            self.module.log(f"  - name : {_image_name}")

            if _image_name == management_container_image:
                result = dict(
                    failed=False,
                    exists=True,
                    container_image=_image_name
                )

        return result

    def container_stop(self, container_name):
        pass

    def container_start(self, container_name):
        pass

    def container_restart(self, container_name):
        pass
