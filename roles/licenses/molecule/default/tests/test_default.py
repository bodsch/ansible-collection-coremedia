
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
import pytest
import os
import testinfra.utils.ansible_runner

from ansible.template import Templar
from ansible.parsing.dataloader import DataLoader

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def base_directory():
    cwd = os.getcwd()

    if 'group_vars' in os.listdir(cwd):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    read_file = None

    for e in ["yml", "yaml"]:
        test_file = f"{file_name}.{e}"
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return f"file={read_file} name={role_name}"


@pytest.fixture()
def get_vars(host):
    """
        parse ansible variables
        - defaults/main.yml
        - vars/main.yml
        - vars/${DISTRIBUTION}.yaml
        - molecule/${MOLECULE_SCENARIO_NAME}/group_vars/all/vars.yml
    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution

    if distribution in ['debian', 'ubuntu']:
        os = "debian"
    elif distribution in ['centos', 'redhat', 'ol']:
        os = "redhat"
    elif distribution in ['arch']:
        os = "archlinux"

    print(f" -> {distribution} / {os}")

    file_defaults      = read_ansible_yaml("{}/defaults/main".format(base_dir), "role_defaults")
    file_vars          = read_ansible_yaml("{}/vars/main".format(base_dir), "role_vars")
    file_distibution   = read_ansible_yaml("{}/vars/{}".format(base_dir, os), "role_distibution")
    file_molecule      = read_ansible_yaml("{}/group_vars/all/vars".format(base_dir), "test_vars")
    # file_host_molecule = read_ansible_yaml("{}/host_vars/{}/vars".format(base_dir, HOST), "host_vars")

    defaults_vars      = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars          = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars   = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars      = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    # host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    # ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


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
    assert d.mode == 0o755

@pytest.mark.parametrize("files", [
    "/etc/coremedia/licenses/cms-license.zip",
    "/etc/coremedia/licenses/mls-license.zip",
    "/etc/coremedia/licenses/rls-license.zip"
])
def test_files(host, files, get_vars):
    g = get_vars

    f = host.file(files)

    assert f.is_file
    assert f.mode == 0o444
    assert f.user == g.get('coremedia_license_user')
