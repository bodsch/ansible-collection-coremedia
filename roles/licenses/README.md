# CoreMedia - Licenses

This role ensures that the CoreMedia licenses are located on the target system.

## usage

```yaml
licenses_directory: '/etc/coremedia/licenses'

licenses_url: ''

licenses_artifacts: []
#  - service: 'mls'
#    file: 'mls-license.zip'
#    destination: 'mls-license.zip'
#  - service: 'cms'
#    file: 'cms-license.zip'
#    destination: 'cms-license.zip'
#  - service: 'rls'
#    file: 'rls-license.zip'
#    destination: 'rls-license.zip'

licenses_user: nobody
licenses_group: "{{ 'nogroup' if ansible_os_family | lower == 'debian' else 'nobody' }}"
```

## examples

**The user and group are not created and must already exist!**

```yaml
licenses_directory: '/etc/coremedia/licenses'

licenses_url: 'http://cm-licenses.test.io/2007.1'

licenses_artifacts:
  - service: 'mls'
    file: 'mls-license.zip'
    destination: 'mls-license.zip'
  - service: 'cms'
    file: 'cms-license.zip'
    destination: 'cms-license.zip'
  - service: 'rls'
    file: 'rls-license.zip'
    destination: 'rls-license.zip'

licenses_user: coremedia
licenses_group: coremedia
```

see also:

- [default](molecule/default/)
- [local-ressource](molecule/local-ressource/)


## tests

deploy licenses from license server, like local nginx.

```bash
make
make verify
make destroy
```

deploy licenses from directory on the ansible controller.

```bash
make -e TOX_SCENARIO=local-ressource
make verify -e TOX_SCENARIO=local-ressource
make destroy -e TOX_SCENARIO=local-ressource
```
