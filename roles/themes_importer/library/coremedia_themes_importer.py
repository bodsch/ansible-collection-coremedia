#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os
import time
from contextlib import suppress

import docker
from ansible.module_utils.basic import AnsibleModule
from docker.errors import DockerException
from docker.types import Mount
from docker.types import LogConfig


class CoremediaFeeder():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.state = module.params.get("state")
        self.container_image = module.params.get("container_image")
        self.themes_archive = module.params.get("themes_archive")
        self.cms_ior = module.params.get("cms_ior")
        self.cms_username = module.params.get("cms_username")
        self.cms_password = module.params.get("cms_password")
        self.mls_ior = module.params.get("mls_ior")
        self.extra_hosts = module.params.get("extra_hosts", {})

    def run(self):
        """
        """
        self.docker_client = docker.DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )

        if not self.container_image:
            return dict(
                failed=True,
                msg="No Container Image defined."
            )

        images = self.container_images(self.container_image)

        if images and isinstance(images, dict):
            """
            """
            # self.module.log(msg=f" - images : {images}")

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

            if self.state == "publish":
                res = {}

                _failed = True
                _changed = False

                error, msg = self.themes_approve()
                # self.module.log(msg=f"- error : {error}")
                approve_ouput = msg
                res.update({"approve": approve_ouput})

                if not error:
                    _failed = False
                    _changed = True

                    error, msg = self.themes_publish()
                    # self.module.log(msg=f"- error : {error}")
                    publish_output = msg
                    res.update({"publish": publish_output})

                    if not error:
                        _failed = False
                        _changed = True
                    else:
                        _failed = True

                return dict(
                    failed=_failed,
                    changed=_changed,
                    msg=res
                )

        return dict(
            failed=True
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

            self.module.log(msg=f" env: {env}")

            cmd = [
                "import-themes",
                "--user", self.cms_username,
                "--password", self.cms_password,
                "--url", self.cms_ior,
                os.path.join("/run/host", themes_archive_file)]

            self.module.log(msg=f" cmd: {cmd}")

            # mount points
            user_dir = Mount(
                target="/run/host",
                source=themes_archive_path,
                type="bind"
            )

            mounts = []
            mounts.append(user_dir)

            error, output = self.run_container(
                "theme-importer", mounts, cmd, env)

            msg = self._parse_import_output(output)

            return error, msg

        else:
            return True, f"Missing Themes Archive {self.themes_archive}."

    def themes_approve(self):
        """
        :return:
        """
        # approve and checkin /Themes
        env = {}
        cmd = []
        cmd.append("bulkpublish")
        cmd.append("--user")
        cmd.append(self.cms_username)
        cmd.append("--password")
        cmd.append(self.cms_password)
        cmd.append("--url")
        cmd.append(self.cms_ior)
        cmd.append("--approve")
        cmd.append("--checkin")
        cmd.append("--folder")
        cmd.append("/Themes")

        error, output = self.run_container("theme-approver", [], cmd, env)

        return error, output

    def themes_publish(self):
        """
        :return:
        """
        # publish /Themes
        env = {}
        cmd = []
        cmd.append("bulkpublish")
        cmd.append("--user")
        cmd.append(self.cms_username)
        cmd.append("--password")
        cmd.append(self.cms_password)
        cmd.append("--url")
        cmd.append(self.cms_ior)
        cmd.append("--publish")
        cmd.append("--folder")
        cmd.append("/Themes")

        error, output = self.run_container("theme-publisher", [], cmd, env)

        e = len([x for x in output if "_FAILED" in x])

        if e > 0:
            error = True

        return error, output

    def run_container(self, name, mounts, cmd, env):
        """
        """
        _output = []
        _failed = False
        container = None

        self.module.log(
            msg=f" run container with image {self.container_image} and command {cmd} and env {env}")

        log_config = LogConfig(
            type=LogConfig.types.JSON,
            config={
                'max-size': '5m',
            }
        )
        try:
            self.module.log(msg="start")
            container = self.docker_client.containers.run(
                image=self.container_image,
                hostname=name,
                name=name,
                mounts=mounts,
                command=cmd,
                entrypoint="/coremedia/tools/bin/cm",
                log_config=log_config,
                detach=True,
                stdout=True,
                stderr=False,
                remove=True,
                environment=env,
                network="coremedia",
                extra_hosts=self.extra_hosts
            )

            for line in container.logs(stream=True):
                entry = line.decode('utf-8').strip()
                # self.module.log(msg=f"  - {entry}")
                _output.append(entry)

        except Exception as e:
            _failed = True
            _msg = f"ERROR : str({e})"
            self.module.log(msg=_msg)
            pass
        except docker.errors.ContainerError as e:
            _failed = True
            _msg = f"ERROR : str({e})"
            self.module.log(msg=_msg)
        except docker.errors.APIError as e:
            _failed = True
            _msg = f"ERROR : str({e})"
            self.module.log(msg=_msg)
        except (DockerException, IOError):
            _failed = True
            _msg = "encountered process error while processing."
            self.module.log(msg=_msg)
        finally:
            self.module.log(msg="ende")

            time.sleep(0.5)
            if container:
                with suppress(DockerException):
                    container.stop()
                    # container.remove()
            pass

        self.module.log(
            msg=f"{_output}"
        )

        return _failed, _output

    def container_images(self, image_name):
        """
        """
        images = {}
        container_filter = {
            "reference": f"{image_name}"
        }

        try:
            for image in self.docker_client.images.list(filters=container_filter):
                images.update({
                    image.attrs.get("RepoTags")[0]: image.attrs.get('Id', None)
                })
            return images
        except Exception as e:
            self.module.log(msg=f"ERROR : str({e})")
            pass

        return None

    def list_containers(self):
        """
        """
        containers = {}
        try:
            for container in self.docker_client.containers.list(all=True):
                containers.update({
                    container.attrs['Id']: container.attrs
                })

            return containers
        except Exception as e:
            self.module.log(msg=f"ERROR : str({e})")
            pass

        return None

    def container(self, container_id):
        """
        """
        if container_id and container_id.isalnum():
            try:
                for container in self.docker_client.containers.list(
                        all=True,
                        filters={"id": container_id}):
                    return container.attrs

            except Exception as e:
                self.module.log(msg=f"ERROR : str({e})")
                pass

        return None

    def container_search(self, name):
        """
        """
        all_containers = self.list_containers()
        if all_containers:
            """
            """
            if isinstance(all_containers, dict):
                for key, value in all_containers.items():
                    container_name = value.get("Name", "")[1:]
                    # self.module.log(msg=f"  - {container_name}")
                    if name == container_name:
                        return self.container(key)

        return None

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


# ===========================================
# Module execution.


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
            themes_archive=dict(
                required=False,
                type="str"
            ),
            cms_ior=dict(
                required=False,
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
            mls_ior=dict(
                required=False,
                type="str"
            ),
            extra_hosts=dict(
                required=False,
                type="dict"
            ),
        ),
        supports_check_mode=True,
    )

    p = CoremediaFeeder(module)
    result = p.run()

    module.log(msg="= result: {}".format(result))
    module.exit_json(**result)


if __name__ == '__main__':
    main()
