win_dns_cache
=============

.. tip:: Ingestion into Splunk.

   **``windows:live_response:dns_cache``**

   * name_rex: ``--win_dns_cache\.jsonl$``
   * path_suffix: ``win_dns_cache``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``DNS_CACHE``
   * normalize: ``ecs_normalize/windows/live_response/dns_cache.vrl``

Description
-----------

Parse dns\_cache.txt from DFIR ORC (ipconfig.exe /displaydns command). Output fields lang depends on the system lang

Timeline
--------

Placeholder table for the messages created for the timeline.

.. list-table::
   :header-rows: 1

   * - Timeline
     - ECS field
     - Message
   * -
     -
     -

Fields
------

Placeholder table for the output fields.

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * -
     -
