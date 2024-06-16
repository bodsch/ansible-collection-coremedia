# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)

import re
__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
    """

    def filters(self):
        return {
            'coremedia_applications': self.coremedia_applications,
            'container_filter_by_name': self.container_filter_by_name,
            'dba_url': self.dba_url,
            'ior_url': self.ior_url,
            'sql_driver': self.sql_driver,
            'sql_dialect': self.sql_dialect,
            'container_mounts': self.container_mounts,
            'spring_configs': self.spring_configs,
        }

    def coremedia_applications(self, data):
        """
        :param data:
        :return:
        """
        result = []

        result = list(data.keys())

        display.v(f" = result {result} {type(result)}")

        return result

    def container_filter_by_name(self, data, container):
        """
        :param data:
        :return:
        """
        display.v(f"container_filter_by_name(self, data, {container})")

        container_names = [x.get("name") for x in data if x.get("name")]
        display.v(f" - found containers: {container_names}")

        filtered_values = list(filter(lambda v: re.match(f'^{container}.*', v), container_names))
        display.v(f" = result: {filtered_values}")

        return filtered_values

    def sql_dialect(self, db_type="mysql"):
        """
        """
        result = None
        if db_type not in ["mysql", "mariadb", "postgres", "mssql", "oracle"]:
            return result

        if db_type == "postgres":
            result = "org.hibernate.dialect.PostgreSQLDialect"
        elif db_type == "mssql":
            result = "org.hibernate.dialect.SQLServer2008Dialect"

        return result

    def sql_driver(self, db_type="mysql"):
        """
        """
        result = None
        if db_type not in ["mysql", "mariadb", "postgres", "mssql", "oracle"]:
            return result

        if db_type in ["mysql", "mariadb"]:
            result = "com.mysql.cj.jdbc.Driver"
        elif db_type == "postgres":
            result = "org.postgresql.Driver"
        elif db_type == "mssql":
            result = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
        elif db_type == "oracle":
            result = "oracle.jdbc.driver.OracleDriver"

        return result

    def dba_url(self, db_type="mysql", db_endpoint="127.0.0.1", db_port="3306", db_schema="coremedia"):
        """
            returns valid dba url for applications and various dba
        """
        result = None

        if db_type not in ["mysql", "mariadb", "postgres", "mssql", "oracle"]:
            return result

        if db_type in ["mysql", "mariadb"]:
            # jdbc:mysql://localhost:3306/coremedia
            result = f"jdbc:mysql://{db_endpoint}:{db_port}/{db_schema}"
        elif db_type == "postgres":
            # jdbc:postgresql://localhost:5432/coremedia
            result = f"jdbc:postgresql://{db_endpoint}:{db_port}/{db_schema}"
        elif db_type == "mssql":
            # jdbc:sqlserver://localhost:1433;databaseName=CM
            result = f"jdbc:sqlserver://{db_endpoint}:{db_port};databaseName={db_schema}"
        elif db_type == "oracle":
            # jdbc:oracle:thin:@localhost:1521:CM
            result = f"jdbc:oracle:thin:@{db_endpoint}:{db_port}:{db_schema}"

        return result

    def ior_url(self, cm_service, hostname, domainname, port):
        """
            returns valid ior url for applications

          cms: "http://content-management-server.{{ coremedia_hosts_domain }}:40180/ior"
          mls: "http://master-live-server.{{ coremedia_hosts_domain }}:40280/ior"
          wfs: "http://workflow-server.{{ coremedia_hosts_domain }}:40380/ior"
          rls1: "http://replication-live-server-01.{{ coremedia_hosts_domain }}:42080/ior"
          rls2: "http://replication-live-server-02.{{ coremedia_hosts_domain }}:42080/ior"
        """
        result = None

        if cm_service not in ["cms", "mls", "wfs", "rls"]:
            return result

        # default ports
        if not port:
            port = "8080"

        if not hostname:
            domainname = None
            hostname = "localhost"

        if len(hostname) > 0 and len(domainname) > 0:
            hostname += f".{domainname}"

        return f"http://{hostname}:{port}/ior"

    def container_mounts(self, data, coremedia_directory={}, application=None, need_mounts=[], append_mounts=[]):
        """
            return a list of dictionaries with mounts for coremedia applications
        """
        _env = coremedia_directory.get("env", None)
        _licenses = coremedia_directory.get("licenses", None)
        _heapdumps = coremedia_directory.get("heapdumps", None)
        _cache = coremedia_directory.get("cache", None)
        _blobcache = coremedia_directory.get("blobcache", None)
        _events_sitemap = coremedia_directory.get("events_sitemap", None)
        _tmp = coremedia_directory.get("tmp", None)

        result = []
        part = {}

        if data in ["content-management-server", "master-live-server", "replication-live-server"] and _licenses:
            part.update(
                source=_licenses,
                target="/coremedia/licenses/",
                type="bind",
                read_only=True,
            )

            result.append(part)

        if "prometheus" in need_mounts and _env:
            result.append(
                dict(
                    source=f"{_env}/{data}/jmx_prometheus.yml",
                    target="/coremedia/prometheus/jmx_prometheus.yml",
                    type="bind",
                    read_only=True,
                    source_handling=dict(
                        create=False,
                        owner="1000",
                        group="1000",
                        mode="0750",
                    )
                )
            )

        if "heapdumps" in need_mounts and _heapdumps:
            result.append(
                dict(
                    source=f"{_heapdumps}/{data}",
                    target="/coremedia/heapdumps",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if "cache" in need_mounts and _cache:
            result.append(
                dict(
                    source=f"{_cache}/{data}",
                    target="/coremedia/cache",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if "blobcache" in need_mounts and _blobcache:
            result.append(
                dict(
                    source=f"{_blobcache}/{data}",
                    target="/coremedia/blobcache",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if "events_sitemap" in need_mounts and _events_sitemap:
            result.append(
                dict(
                    source=f"{_events_sitemap}/{data}",
                    target="/coremedia/eventsSitemap",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if "tmp" in need_mounts and _tmp:
            result.append(
                dict(
                    source=f"{_tmp}/{data}",
                    target="/coremedia/var/tmp",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if "state" in need_mounts and _env:
            result.append(
                dict(
                    source=f"{_env}/{data}/state",
                    target="/coremedia/state",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="1000",
                        group="1000",
                        mode="0770",
                    )
                )
            )

        if re.match('^solr.*', data) and "data" in need_mounts and _env:
            result.append(
                dict(
                    source=f"{_env}/{data}/data",
                    target="/var/solr",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="8983",
                        group="8983",
                    )
                )
            )

        if re.match('^mongodb.*', data) and "data" in need_mounts and _env:
            result.append(
                dict(
                    source=f"{_env}/{data}/data",
                    target="/data/db",
                    type="bind",
                    read_only=False,
                    source_handling=dict(
                        create=True,
                        owner="999",
                    )
                )
            )

        if re.match('^cadvisor.*', data) and "data" in need_mounts:
            result.append(
                dict(
                    source="/",
                    target="/rootfs",
                    type="true",
                    read_only=True,
                ),
                dict(
                    source="/var/run",
                    target="/var/run",
                    type="true",
                    read_only=True,
                ),
                dict(
                    source="/sys",
                    target="/sys",
                    type="true",
                    read_only=True,
                ),
                dict(
                    source="/var/lib/docker",
                    target="/var/lib/docker",
                    type="true",
                    read_only=True,
                ),
                dict(
                    source="/dev/disk",
                    target="/dev/disk",
                    type="true",
                    read_only=True,
                ),
            )

        properties = [x for x in need_mounts if re.search(".*.properties", x)]
        if len(properties) > 0 and _env:
            for i in properties:
                source = f"{_env}/{data}/{i}"
                if application:
                    source = f"{_env}/{application}/{i}"
                result.append(
                    dict(
                        source=source,
                        target=f"/coremedia/properties/corem/{i}",
                        type="bind",
                        read_only=False,
                        source_handling=dict(
                            create=False,
                            owner="1000",
                            group="1000",
                            mode="0750",
                        )
                    )
                )

        return result

    def spring_configs(self, data, properties):
        """
        """
        display.v(f"spring_configs(self, {data}, {properties})")

        result = None
        arr = []

        for i in properties:
            arr.append(f"file:./properties/corem/{i}")

        if len(arr) > 0:
            result = ",".join(arr)

        display.v(f" = result: {result}")
        return result
