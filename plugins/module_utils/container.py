#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os
import time
from contextlib import suppress
import docker
from docker.errors import DockerException
from docker.types import LogConfig


class Container():
    """
    """

    def __init__(self, module):
        """
        """
        self.module = module

        self.module.log("Container::__init__")

        self.docker_client = docker.DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )

    def run_container(self, container_image, name, network="coremedia", extra_hosts={}, mounts=[], cmd=[], env={}):
        """
        """
        _output = []
        _status_code = 500
        _status_msg = None
        container = None

        self.module.log(
            msg=f"run container with image {container_image} and command {cmd}.")

        log_config = LogConfig(
            type=LogConfig.types.JSON,
            config={
                'max-size': '5m',
            }
        )

        try:
            container = self.docker_client.containers.run(
                image=container_image,
                hostname=name,
                name=name,
                command=cmd,
                mounts=mounts,
                entrypoint="/coremedia/tools/bin/cm",
                log_config=log_config,
                detach=True,
                stdout=True,
                stderr=True,
                remove=True,
                environment=env,
                network=network,
                extra_hosts=extra_hosts
            )

            _status_code = 200
            _status_msg = None

            for line in container.logs(stream=True):
                self.module.log(msg=f" - {line}")
                entry = line.decode('utf-8').strip()

                if "DOCKER ENTRYPOINT" not in entry:
                    _output.append(entry)

        except docker.errors.ContainerError as e:
            # _failed = True
            _status_code = e.status_code
            _status_msg = e.explanation
            self.module.log(f"ERROR (ContainerError) : {_status_code} - {e.explanation}")
        except docker.errors.APIError as e:
            # _failed = True
            _status_code = e.status_code
            _status_msg = e.explanation
            self.module.log(f"ERROR (APIError) : {_status_code} - {e.explanation}")
        except (DockerException, IOError):
            self.module.log(
                msg="[docker]: encountered process error while processing.")
        except Exception as e:
            # _failed = True
            _msg = f"ERROR (Exception) : {str(e)}"
            self.module.log(msg=_msg)
            pass
        finally:
            if container:
                running_container = self.docker_client.containers.get(name)
                # self.module.log(f"  -> {running_container.id} {running_container.name} {running_container.status}")
                # stop and delete only running container
                if running_container and running_container.status in ["running"]:
                    time.sleep(0.5)

                    with suppress(DockerException):
                        container.stop()
                    try:
                        container.remove()
                    except Exception as e:
                        # _failed = True
                        _msg = f"ERROR (Exception) : {str(e)}"
                        self.module.log(msg=_msg)
                        _status_code = e.status_code
                        _status_msg = e.explanation
                        self.module.log(f"ERROR (Exception) : {_status_code} - {e.explanation}")
                        pass
            pass

        self.module.log(f"  - output : {_output}")

        return _output, _status_code, _status_msg

    def exec_container(self, container_id, cmd):
        """
    #         Run a command inside this container. Similar to docker exec
    #
    #         exec_run(cmd,
    #             stdout=True,
    #             stderr=True,
    #             stdin=False,
    #             tty=False,
    #             privileged=False,
    #             user='',
    #             detach=False,
    #             stream=False,
    #             socket=False,
    #             environment=None,
    #             workdir=None,
    #             demux=False)
        """
        self.module.log(f" run command {cmd} inside the container.")

        output = None
        _status_code = 500
        _status_msg = None

        try:
            container = self.docker_client.containers.get(container_id)

            # self.module.log("---- exec_run() --------------")
            _status_code, output = container.exec_run(
                cmd=cmd,
                detach=False,
            )

            self.module.log(msg=f" - _status_code : {_status_code}")
            self.module.log(msg=f" - output       : {output}")

            if _status_code == 0:
                """
                """
                _status_code = 200

                # pattern = re.compile(
                #     r".*<h1>CoreMedia Content Feeder Administration</h1><p>(?P<output>.*?)</p>.*")
                #
                # result = re.search(pattern, output.decode('utf-8'))
                # output_string = result.group('output')

                # self.module.log(msg=f" - exit_code : {exit_code}")
                # self.module.log(msg=f" - output    : {output_string}")
            else:
                cmd_string = ' '.join(cmd)
                output = f"There was an error when calling '{cmd_string}'"

        except docker.errors.ContainerError as e:
            # _failed = True
            _status_code = e.status_code
            _status_msg = e.explanation
            self.module.log(f"ERROR (ContainerError) : {_status_code} - {e.explanation}")
        except docker.errors.APIError as e:
            # _failed = True
            _status_code = e.status_code
            _status_msg = e.explanation
            self.module.log(f"ERROR (APIError) : {_status_code} - {e.explanation}")
        except (DockerException, IOError):
            self.module.log(
                msg="[docker]: encountered process error while processing.")
        except Exception as e:
            # _failed = True
            _msg = f"ERROR (Exception) : {str(e)}"
            self.module.log(msg=_msg)
            pass
        finally:
            time.sleep(0.5)
            pass

        self.module.log(f"  - output : {output}")

        return output, _status_code, _status_msg

    def write_properties_file(self, filename, data):
        """
            sql.store.driver = org.postgresql.Driver
            sql.store.url = jdbc:postgresql://bce-cmpdb-sv04.tik.intern:5432/replication_live_server
            sql.store.user = replication_live_server
            sql.store.password = RdhYNZC6bnx2lzuk9sYFkZ7dTjcGZsaFOrHoqhaVvK
        """
        if isinstance(data, dict):
            self.module.log(msg=f"  - {data}")
            with open(filename, "w") as f:
                f.write("# written by ansible\n")
                if len(data) > 0:
                    f.write("# SQL STORE\n")
                    sql_store_driver = data.get("driver", None)
                    sql_store_url = data.get("url", None)
                    sql_store_username = data.get("username", None)
                    sql_store_password = data.get("password", None)

                    if sql_store_driver:
                        f.write(f"sql.store.driver       = {sql_store_driver}\n")
                    if sql_store_url:
                        f.write(f"sql.store.url          = {sql_store_url}\n")
                    if sql_store_username:
                        f.write(f"sql.store.user         = {sql_store_username}\n")
                    if sql_store_password:
                        f.write(f"sql.store.password     = {sql_store_password}\n")

                os.chown(filename, 1000, 1000)

        # self.environments_file =

    def environments_from_files(self, environments_files=[]):
        """
        """
        lines = []

        for env_file in environments_files:
            if os.path.isfile(env_file):
                self.module.log(f"  - read file: {env_file}")
                with open(env_file) as f:
                    for line in f:
                        # self.module.log(msg=f"  - {line}")
                        if len(line) > 1 and not line.startswith("#") and 'WAIT_HOSTS' not in line:
                            line = line.strip()  # or some other preprocessing
                            lines.append(line)   # storing everything in memory!

        return lines

    def container_images(self, image_name):
        """
        """
        self.module.log(f"Container::container_images({image_name})")

        images = {}
        filter = {
            "reference": f"{image_name}"
        }

        try:
            for image in self.docker_client.images.list(filters=filter):
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
        self.module.log("Container::list_containers()")

        containers = {}
        try:
            for container in self.docker_client.containers.list(all=True):
                containers.update({
                    container.attrs['Id']: container.attrs
                })

            # self.module.log(msg=f"  type {type(containers)}")
            return containers

        except Exception as e:
            self.module.log(msg=f"ERROR : str({e})")
            pass

        return None

    def container(self, container_id):
        """
        """
        self.module.log(f"Container::container({container_id})")

        result = None

        if container_id and container_id.isalnum():
            try:
                for container in self.docker_client.containers.list(all=True, filters={"id": container_id}):
                    result = container.attrs

            except Exception as e:
                self.module.log(msg=f"ERROR : str({e})")
                pass

        return result

    def container_search(self, name):
        """
        """
        self.module.log(f"Container::container_search({name})")
        all_containers = self.list_containers()
        if all_containers:
            """
            """
            # self.module.log(msg=f"  type {type(all_containers)}")
            if isinstance(all_containers, dict):
                container_id = None

                result = {k: v for k, v in all_containers.items() if v.get('Name', '')[1:] == name}
                # self.module.log(msg=f"  result {result}")
                if result:
                    container_id = list(result.keys())[0]
                else:
                    result = {k: v for k, v in all_containers.items() if v.get('Name', '')[1:].startswith(name)}
                    # self.module.log(msg=f"  result {result}")
                    container_id = list(result.keys())[0]

                if container_id:
                    self.module.log(msg=f"  - found container id: {container_id}")
                    return self.container(container_id)

        return None

    def container_stop(self, name):
        """
            :return:
        """
        self.module.log(f"Container::container_stop({name})")

        container = self.container_search(name)

        if container:
            container_id = container.get("Id", None)

            self.module.log(f" = stop container with id {container_id}")

            if container_id:
                for container in self.docker_client.containers.list(all=True, filters={"id": container_id}):
                    container.stop()

                return True, 'stop command completed successfully.'
            else:
                return False, "unknow container id."
        else:
            return False, f"no running container {name} found."

    def container_start(self, name):
        """
            :return:
        """
        self.module.log(f"Container::container_start({name})")

        container = self.container_search(name)

        if container:
            container_id = container.get("Id", None)

            self.module.log(f" = start container with id {container_id}")

            if container_id:
                for container in self.docker_client.containers.list(all=True, filters={"id": container_id}):
                    container.start()

                return True, 'start command completed successfully.'
            else:
                return False, "unknow container id."
        else:
            return False, f"no running container {name} found."

    def container_restart(self, name):
        """
            :return:
        """
        self.module.log(f"Container::container_restart({name})")

        container = self.container_search(name)

        if container:
            container_id = container.get("Id", None)

            self.module.log(f" = restart conatiner with id {container_id}")

            if container_id:
                for container in self.docker_client.containers.list(all=True, filters={"id": container_id}):
                    container.restart()

                return True, 'restart command completed successfully.'
            else:
                return False, "unknow container id."
        else:
            return False, f"no running container {name} found."

    def parse_container_output(self, output, valid_arr):
        """
        """
        result = []
        for line in output:
            if line.startswith(tuple(valid_arr)):
                result.append(line)

        return result
