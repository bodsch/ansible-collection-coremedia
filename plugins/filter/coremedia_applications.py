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
            'coremedia_container': self.coremedia_container,
            'coremedia_dba_url': self.coremedia_dba_url,
            'coremedia_ior_url': self.coremedia_ior_url,
            'sql_driver': self.sql_driver,
            'sql_dialect': self.sql_dialect,
            'coremedia_mounts': self.coremedia_mounts,
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

    def coremedia_container(self, data, container):
        """
        :param data:
        :return:
        """
        display.v(f"coremedia_container(self, data, {container})")
        result = []

        container_names = [x.get("name") for x in data if x.get("name")]
        display.v(f" - found containers: {container_names}")

        filtered_values = list(filter(lambda v: re.match(f'^{container}.*', v), container_names))
        display.v(f" = result: {filtered_values}")

        return filtered_values

        # if container in container_names:
        #     result = True
        #     display.v(f" = result {container}: {result} {type(result)}")
        #
        # result = len([x for x in data if x.get("name") == container]) != 0
        #
        # display.v(f" = result {container}: {result} {type(result)}")
        # return result

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

    def coremedia_dba_url(self, db_type="mysql", db_endpoint="127.0.0.1", db_port="3306", db_schema="coremedia"):
        """
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
            result = "jdbc:oracle:thin:@{db_endpoint}:{db_port}:{db_schema}"

        return result

    def coremedia_ior_url(self, cm_service, hostname, domainname, port):
        """
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

    def coremedia_mounts(self, data, coremedia_directory={}, need_mounts=[], append_mounts=[]):
        """
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
                source = _licenses,
                target = "/coremedia/licenses/",
                type = "bind",
                read_only = True,
            )

            result.append(part)

        if "prometheus" in need_mounts and _env:
            result.append(
                dict(
                    source = f"{_env}/{data}/jmx_prometheus.yml",
                    target = "/coremedia/prometheus/jmx_prometheus.yml",
                    type = "bind",
                    read_only = True,
                    source_handling = dict(
                      create = False,
                      owner = "1000",
                      group = "1000",
                      mode = "0750",
                    )
                )
            )

        if "heapdumps" in need_mounts and _heapdumps:
            result.append(
                dict(
                    source = f"{_heapdumps}/{data}",
                    target = "/coremedia/heapdumps",
                    type = "bind",
                    read_only = False,
                    source_handling = dict(
                      create = True,
                      owner = "1000",
                      group = "1000",
                      mode = "0770",
                    )
                )
            )

        if "cache" in need_mounts and _cache:
            result.append(
                dict(
                    source = f"{_cache}/{data}",
                    target = "/coremedia/cache",
                    type = "bind",
                    read_only = False,
                    source_handling = dict(
                      create = True,
                      owner = "1000",
                      group = "1000",
                      mode = "0770",
                    )
                )
            )

        if "blobcache" in need_mounts and _blobcache:
            result.append(
                dict(
                    source = f"{_blobcache}/{data}",
                    target = "/coremedia/blobcache",
                    type = "bind",
                    read_only = False,
                    source_handling = dict(
                      create = True,
                      owner = "1000",
                      group = "1000",
                      mode = "0770",
                    )
                )
            )

        if "events_sitemap" in need_mounts and _events_sitemap:
            result.append(
                dict(
                    source = f"{_events_sitemap}/{data}",
                    target = "/coremedia/eventsSitemap",
                    type = "bind",
                    read_only = False,
                    source_handling = dict(
                      create = True,
                      owner = "1000",
                      group = "1000",
                      mode = "0770",
                    )
                )
            )

        if "tmp" in need_mounts and _tmp:
            result.append(
                dict(
                    source = f"{_tmp}/{data}",
                    target = "/coremedia/var/tmp",
                    type = "bind",
                    read_only = False,
                    source_handling = dict(
                      create = True,
                      owner = "1000",
                      group = "1000",
                      mode = "0770",
                    )
                )
            )

        return result
