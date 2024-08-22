#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container
from ansible_collections.bodsch.coremedia.plugins.module_utils.coremedia import Coremedia


class CoremediaResetCAEFeeder:
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")
        self.management_container_image = module.params.get("management_container_image")
        self.feeder_name = module.params.get("feeder_name")
        self.environments_file = module.params.get("environments_file")
        self.extra_hosts = module.params.get("extra_hosts")

    def run(self):
        """
        """
        _failed = True
        _changed = False
        _msg = "module init."

        self.container = Container(self.module)

        management_container_image = self.container.container_images(image_name=self.management_container_image)

        if not management_container_image:

            return dict(
                failed=True,
                changed=False,
                msg=f"Container Image {self.management_container_image} not found."
            )

        self.coremedia = Coremedia(self.module)

        feeder_status = self.coremedia.feeder_status(self.feeder_name)
        # self.module.log(f"  - feeder_status: {feeder_status}")

        env = self.container.environments_from_files([self.environments_file])

        # self.module.log(f"    feeder_name       : {self.feeder_name}")
        # self.module.log(f"    environments file : {self.environments_file}")
        # self.module.log(f"    env               : {env}")

        feeder_status, status_code, status_msg = self.feeder_name_status(env)
        # self.module.log(f"   feeder status      : {feeder_status[0]}")

        if str(status_code) != "200":
            return dict(
                failed=True,
                msg=status_msg
            )

        matches = len(
            [match for match in feeder_status if " will not be reset " in match]) > 0

        if self.module.check_mode:
            _failed = False
            _changed = False
            _msg = f"we are in check mode, feeder can be reset: {feeder_status[0]}"
            self.module.log(_msg)

            return dict(
                failed=_failed,
                changed=_changed,
                msg=_msg
            )

        if self.state == "reset":
            if matches:
                """
                """
                feeder_status, status_code, status_msg = self.feeder_name_reset(env)
                # self.module.log(msg=f"  - feeder status: {feeder_status[0]}")

            matches = len(
                [match for match in feeder_status if
                 " will be reset when restarted" in match]) > 0

            if matches:
                """
                """
                result, msg = self.feeder_name_restart()
                time.sleep(2)

                if result:
                    _failed = False
                    _changed = True

                _msg = msg

        return dict(
            failed=_failed,
            changed=_changed,
            msg=_msg
        )

    def feeder_name_status(self, env):
        """
        """
        cmd = []
        cmd.append("resetcaefeeder")
        cmd.append("status")

        output, status_code, status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name=f"{self.feeder_name}-status",
            cmd=cmd,
            env=env
        )

        # self.module.log(msg=f"  - output      : {output}")
        # self.module.log(msg=f"  - status_code : {status_code}")
        # self.module.log(msg=f"  - status_msg  : {status_msg}")

        return output, status_code, status_msg

    def feeder_name_reset(self, env):
        """
        """
        cmd = []
        cmd.append("resetcaefeeder")
        cmd.append("reset")

        output, status_code, status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name=f"{self.feeder_name}-reset",
            # extra_hosts=self.extra_hosts,
            cmd=cmd,
            env=env
        )

        # self.module.log(msg=f"  - output      : {output}")
        # self.module.log(msg=f"  - status_code : {status_code}")
        # self.module.log(msg=f"  - status_msg  : {status_msg}")

        return output, status_code, status_msg

    def feeder_name_restart(self):
        """
        """
        self.module.log(msg="feeder_name_restart()")
        self.module.log(msg=f"  - {self.feeder_name}")

        container = self.container.container_search(self.feeder_name)

        if container:
            self.feeder_name = container.get("Name", '')[1:]   # cut first char

        state, msg = self.container.container_restart(self.feeder_name)

        return state, msg


def main():
    """
    """
    args = dict(
        state=dict(
            default="verify",
            choices=["verify", "reset"]
        ),
        management_container_image=dict(
            required=True,
            type="str"
        ),
        feeder_name=dict(
            required=True,
            type="str"
        ),
        environments_file=dict(
            required=True,
            type="str"
        ),
        extra_hosts=dict(
            required=False,
            type="dict",
        ),
    )
    module = AnsibleModule(
        argument_spec=args,
        supports_check_mode=True,
    )

    p = CoremediaResetCAEFeeder(module)
    result = p.run()

    module.log(f"= result: {result}")
    module.exit_json(**result)


if __name__ == '__main__':
    main()
