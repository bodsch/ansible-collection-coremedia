# CoreMedia Contentfeeder

## requirements

### Ansible Collection

- bodsch.coremedia
 
## usage

### reset Content Feeder

```yaml
- name: coremedia reset Content Feeder
  hosts: coremedia
  gather_facts: true
  become: true

  roles:
    - role: bodsch.coremedia.contentfeeder
      vars:
        contentfeeder:
          name: "content-feeder"
          command: "reset"
      tags:
        - coremedia_reset_contentfeeder
```


### example implementation

```yaml
- name: coremedia reset Content Feeder
  hosts: coremedia
  gather_facts: true
  become: true

  vars:
    contentfeeder:
      name: "content-feeder"
      command: "reset"
      feeder_admin:
        username: "feeder"
        password: "feeder"

  pre_tasks:
    - name: define feeder
      ansible.builtin.set_fact:
        _contentfeeder: "{{ container | bodsch.coremedia.coremedia_container('content-feeder' | default('')) }}"

  roles:
    - role: bodsch.coremedia.contentfeeder
      when:
        - _contentfeeder
      tags:
        - coremedia_reset_contentfeeder
```
