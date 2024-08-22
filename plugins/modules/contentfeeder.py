#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container


class CoremediaResetContentfeeder():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")

        self.feeder_name = module.params.get("feeder_name")
        self.feeder_admin_username = module.params.get("feeder_admin", {}).get("username", "feeder")
        self.feeder_admin_password = module.params.get("feeder_admin", {}).get("password", "feeder")

    def run(self):
        """
        """
        _failed = True
        _changed = False
        _msg = "module init."

        self.container = Container(self.module)
        container = self.container.container_search(self.feeder_name)
        # self.module.log(f"  - container : {container}")

        if container and isinstance(container, dict):
            """
            """
            container_id = container.get('Id', None)
            # self.module.log(msg=f" - id : {container_id}")
            if container_id:
                error, msg = self.contentfeeder_reset(container_id)

                if not error:
                    result, restart_msg = self.feeder_name_restart()

                    if result:
                        _failed = False
                        _changed = True

                        if isinstance(msg, list):
                            msg.append(restart_msg)

                    _msg = msg
                else:
                    _msg = msg

        return dict(
            failed=_failed,
            changed=_changed,
            msg=_msg
        )

    def contentfeeder_reset(self, container_id):
        """
            docker exec content-feeder curl -v -ufeeder:feeder http://localhost:8080/admin?action=stop
            docker exec content-feeder curl -v -ufeeder:feeder http://localhost:8080/admin?action=clearCollection (bearbeitet)
        """
        result_string = []

        cmd = []
        cmd.append("curl")
        cmd.append("--silent")
        cmd.append("--user")
        cmd.append(f"{self.feeder_admin_username}:{self.feeder_admin_password}")

        cmd_stop = cmd + ["http://localhost:8080/admin?action=stop"]
        cmd_clear = cmd + ["http://localhost:8080/admin?action=clearCollection"]

        if self.module.check_mode:
            exit_code = 0
            result_string = "check_mode"

            self.module.log("we are in check mode, otherwise this would be called")
            self.module.log(f"  - stop : '{cmd_stop}'")
            self.module.log(f"  - clear: '{cmd_clear}'")

            return (exit_code != 0), result_string

        # send 'stop'
        # expect output : 'The stop command was sent to the feeder.'
        output, exit_code, status_msg = self.container.exec_container(container_id, cmd_stop)

        if str(exit_code) == "200":
            output = self._parse_output(output)

            result_string.append(output)

            # send 'clearCollection'
            # expect output : 'The Search Engine index was cleared.'
            output, exit_code, status_msg = self.container.exec_container(container_id, cmd_clear)

            if str(exit_code) == "200":
                output = self._parse_output(output)
                result_string.append(output)

        return (exit_code != 200), result_string

    def _parse_output(self, data):

        pattern = re.compile(
            r".*<h1>CoreMedia Content Feeder Administration</h1><p>(?P<output>.*?)</p>.*")

        result = re.search(pattern, data.decode('utf-8'))
        output_string = result.group('output')

        return output_string

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
    :return:
    """
    args = dict(
        state=dict(
            default="verify",
            choices=["verify", "reset"]
        ),
        feeder_name=dict(
            required=True,
            type="str"
        ),
        feeder_admin=dict(
            required=False,
            type="dict"
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

    p = CoremediaResetContentfeeder(module)
    result = p.run()

    module.log(msg=f"= result: {result}")
    module.exit_json(**result)


if __name__ == '__main__':
    main()
