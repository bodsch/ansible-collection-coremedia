# CoreMedia CAEFeeder

## requirements

## usage

### reset CAE Feeder

```yaml
- name: coremedia reset CAEFeeder
  hosts: coremedia
  gather_facts: true
  become: true

  pre_tasks:
    - name: define feeder
      ansible.builtin.set_fact:
        _caefeeder: "{{ container | bodsch.coremedia.coremedia_container('caefeeder-live' | default('')) }}"

  roles:
    - role: bodsch.coremedia.caefeeder
      vars:
        management_container:
          name: "{{ container_registry_dev }}/coremedia/management-tools:{{ container_tags.coremedia }}"
        caefeeder:
          name: "caefeeder-live"
          command: "reset"
      when:
        - _caefeeder
```
