#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.coremedia.plugins.module_utils.container import Container
from docker.types import Mount


class CoremediaThemesImporter():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")

        self.management_container_image = module.params.get("management_container_image")
        self.themes_archive = module.params.get("themes_archive")
        self.content_server_ior = module.params.get("content_server_ior")
        self.coremedia_admin = module.params.get("coremedia_admin", {})
        self.cm_admin_username = self.coremedia_admin.get("username", "admin")
        self.cm_admin_password = self.coremedia_admin.get("password", "admin")
        self.cms_ior = self.content_server_ior.get("cms")
        self.mls_ior = self.content_server_ior.get("mls")

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

        _failed = True
        _changed = False

        if self.state == "import":

            error, msg = self.themes_import()

            if not error:
                _failed = False
                _changed = True
            else:
                _failed = True
                _changed = False

            return dict(
                failed=_failed,
                changed=_changed,
                msg=msg
            )

        if self.state == "approve":

            error, msg = self.themes_approve()

            if not error:
                _failed = False
                _changed = True
            else:
                _failed = True
                _changed = False

            return dict(
                failed=_failed,
                changed=_changed,
                msg=msg
            )

        if self.state == "publish":

            error, msg = self.themes_publish()

            if not error:
                _failed = False
                _changed = True
            else:
                _failed = True
                _changed = False

            return dict(
                failed=_failed,
                changed=_changed,
                msg=msg
            )

    def themes_import(self):
        """
        """
        self.module.log(msg=f" archive: {self.themes_archive}")

        if self.themes_archive and os.path.isfile(self.themes_archive):
            themes_archive_path = os.path.dirname(self.themes_archive)
            themes_archive_file = os.path.basename(self.themes_archive)

            self.module.log(msg=f" path: {themes_archive_path}")
            self.module.log(msg=f" file: {themes_archive_file}")

            env = dict(
                CMS_IOR_URL=self.cms_ior,
                MLS_IOR_URL=self.mls_ior
            )

            cmd = [
                "import-themes",
                "--user", self.cm_admin_username,
                "--password", self.cm_admin_password,
                "--url", self.cms_ior,
                os.path.join("/run/host", themes_archive_file)]

            # mount points
            user_dir = Mount(
                target="/run/host",
                source=themes_archive_path,
                type="bind"
            )

            mounts = []
            mounts.append(user_dir)

            output, status_code, status_msg = self.container.run_container(
                container_image=self.management_container_image,
                name="theme-importer",
                mounts=mounts,
                cmd=cmd,
                env=env
            )

            if int(status_code) == 200:
                error = False

            msg = self._parse_import_output(output)

            return error, msg

        else:
            return True, f"Missing Themes Archive {self.themes_archive}."

    def themes_approve(self):
        """
            approve and checkin /Themes
        """
        error = False

        env = {}
        cmd = []
        cmd.append("bulkpublish")
        cmd.append("--user")
        cmd.append(self.cm_admin_username)
        cmd.append("--password")
        cmd.append(self.cm_admin_password)
        cmd.append("--url")
        cmd.append(self.cms_ior)
        cmd.append("--approve")
        cmd.append("--checkin")
        cmd.append("--folder")
        cmd.append("/Themes")

        mounts = []

        output, status_code, status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name="theme-approver",
            mounts=mounts,
            cmd=cmd,
            env=env
        )

        if int(status_code) == 200:
            error = False

        # error, output = self.container.run_container("theme-approver", [], cmd, env)

        return error, output

    def themes_publish(self):
        """
            publish /Themes
        """
        error = False

        env = {}
        cmd = []
        cmd.append("bulkpublish")
        cmd.append("--user")
        cmd.append(self.cm_admin_username)
        cmd.append("--password")
        cmd.append(self.cm_admin_password)
        cmd.append("--url")
        cmd.append(self.cms_ior)
        cmd.append("--publish")
        cmd.append("--folder")
        cmd.append("/Themes")

        mounts = []

        output, status_code, status_msg = self.container.run_container(
            container_image=self.management_container_image,
            name="theme-publisher",
            mounts=mounts,
            cmd=cmd,
            env=env
        )

        e = len([x for x in output if "_FAILED" in x])

        if e > 0:
            error = True

        return error, output

    def _parse_import_output(self, output):
        """
            Started ThemeImporterClient ...
            Import themes to /Themes
            Created Theme in ...
            Done.
            Theme importer success
        """
        result = []

        pos = [
            "Started ThemeImporterClient",
            "Import themes to /Themes",
            "Created Theme in",
            "Done.",
            "Theme importer success"
        ]

        for line in output:
            if line.startswith(tuple(pos)):
                result.append(line)

        return result


def main():
    """
    """
    args = dict(
        state=dict(
            default="import",
            choices=["import", "approve", "publish"]
        ),
        management_container_image=dict(
            required=True,
            type="str"
        ),
        themes_archive=dict(
            required=False,
            type="str"
        ),
        content_server_ior=dict(
            required=True,
            type="dict"
        ),
        coremedia_admin=dict(
            required=True,
            type="dict",
        ),
        environments_file=dict(
            required=False,
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

    p = CoremediaThemesImporter(module)
    result = p.run()

    module.log(msg="= result: {}".format(result))
    module.exit_json(**result)


if __name__ == '__main__':
    main()
