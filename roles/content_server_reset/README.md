# CoreMedia Content Server Reset

## requirements

### Ansible Rolle

- docker
- container

### Ansible Collection

- bodsch.coremedia
 
## usage

```yaml
- name: reset content-management-server on cms.cm.local
  hosts: cms.cm.local
  gather_facts: true
  become: true
  remote_user: ansible

  vars:
    _content_server_reset: false
    container_filter:
      by: "image"
      names:
        - "{{ container_registry.host }}/coremedia/content-server:{{ coremedia_container_tags.content_server }}"
    content_server_reset:
      content_server: "content-management-server"
      content_server_ior: "{{ coremedia_ior['cms'] }}"
      sql_store:
        driver: "{{ coremedia_sql_driver['cms'] }}"
        url: "{{ coremedia_dba['cms'] }}"
        username: "{{ coremedia_dba_user['cms'] }}"
        password: "{{ coremedia_dba_user['cms'] }}"

  pre_tasks:
    - name: define server reset
      ansible.builtin.set_fact:
        _content_server_reset: "{{ container | bodsch.coremedia.coremedia_container(content_server_reset.content_server | default('')) }}"

  roles:
    - role: bodsch.coremedia.content_server_reset
      tags:
        - coremedia_container
        - coremedia_content_server_container
      when:
        - _content_server_reset
```
