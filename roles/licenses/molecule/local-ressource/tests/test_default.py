import pytest
import os
import yaml
import testinfra.utils.ansible_runner

from ansible.template import Templar
from ansible.parsing.dataloader import DataLoader

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def get_vars(host):
    defaults_files = "file=../../defaults/main.yml name=role_defaults"
    vars_files = "file=../../vars/main.yml name=role_vars"

    ansible_vars = host.ansible(
        "include_vars",
        defaults_files)["ansible_facts"]["role_defaults"]

    ansible_vars.update(host.ansible(
        "include_vars",
        vars_files)["ansible_facts"]["role_vars"])

    templar = Templar(loader=DataLoader(), variables=ansible_vars)

    return templar.template(ansible_vars, fail_on_undefined=False)


@pytest.mark.parametrize("dirs", [
    "/etc/coremedia",
    "/etc/coremedia/licenses"
])
def test_directories(host, dirs, get_vars):
    g = get_vars
    d = host.file(dirs)
    assert d.is_directory
    assert d.exists
    assert d.user == g.get('coremedia_license_user')
    # assert d.group == g.get('coremedia_license_group')
    assert d.mode == 0o750

@pytest.mark.parametrize("files", [
    "/etc/coremedia/licenses/cms.zip",
    "/etc/coremedia/licenses/mls.zip",
    "/etc/coremedia/licenses/rls.zip"
])
def test_files(host, files, get_vars):
    g = get_vars

    f = host.file(files)
    assert f.exists
    assert f.is_file
    assert f.mode == 0o660
    assert f.user == g.get('coremedia_license_user')
    # assert f.group == g.get('coremedia_license_group')
