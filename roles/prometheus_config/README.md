# ansible rolle `prometheus-config`

The role is used to roll out different configurations for the [jmx_prometheus exporter](https://github.com/prometheus/jmx_exporter) of CoreMedia applications.


These beans could be interesting for the monitoring of CoreMedia applications:

- CoreMedia Caches (DateView, CacheKey, Uapi, Heap)
- TransformedBlobCache
- Tomcat ThreadPools (they seemed to be named differently, depending on the tomcat configuration -> add to bean queries)

Feel free to add more ObjectNames to this list.


Interesting beans can be found in the old [CoreMedia monitoring repository](
https://github.com/CoreMedia/monitoring/blob/master/doc/de/jmx.md#coremedia-jmx-beans).
