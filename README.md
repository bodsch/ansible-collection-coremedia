# Ansible Collection - bodsch.coremedia

Documentation for the collection.

## Roles

| Role                                                                            | | Description |
|:---------------------------------------------------------------------------     | :---- | :---- |
| [bodsch.coremedia.prometheus_config](./roles/prometheus_config/README.md)       |       |       |
| [bodsch.coremedia.licenses](./roles/licenses/README.md)                         |       |       |
| [bodsch.coremedia.content_server_reset](./roles/content_server_reset/README.md) |       |       |
| [bodsch.coremedia.caefeeder](./roles/caefeeder/README.md)                       |       |       |
| [bodsch.coremedia.contentfeeder](./roles/contentfeeder/README.md)               |       |       |
| [bodsch.coremedia.themes_importer](./roles/themes_importer/README.md)           |       |       |

## Modules

| Module                                                                     |       | Description |
|:---------------------------------------------------------------------------| :---- | :---- |
| `bodsch.coremedia.content_server_state`                                    |       | Returns the current status of a content server |
| `bodsch.coremedia.content_server_reset`                                    |       | Resets the database of a content server      |
| `bodsch.coremedia.caefeeder`                                               |       | Resets a CAE Feeder      |
| `bodsch.coremedia.contentfeeder`                                           |       | Resets a Content Feeder      |
| `bodsch.coremedia.themes_importer`                                         |       | Import, Approve and Publissh Themes      |

### planned
 - content-import
 - management
