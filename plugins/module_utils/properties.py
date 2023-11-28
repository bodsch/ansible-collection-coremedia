#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2023, Bodo Schulz <bodo@boone-schulz.de>

from __future__ import absolute_import, division, print_function

import os

def write_properties_file(module, filename, data):
    """
    """
    if isinstance(data, dict):
        module.log(msg=f"  - {data}")
        with open(filename, "w") as f:
            f.write("# written from ansible\n")
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


def environments_from_file(module, filename):
    """
    """
    lines = []
    if os.path.isfile(filename):
        with open(filename) as f:
            for line in f:
                module.log(msg=f"  - {line}")
                if len(line) > 1 and not line.startswith("#") and 'WAIT_HOSTS' not in line:
                    line = line.strip()     # or some other preprocessing
                    lines.append(line)      # storing everything in memory!

    return lines
