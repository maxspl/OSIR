win_dns_records
===============

.. tip:: Ingestion into Splunk.

   **``windows:live_response:dns_records``**

   * name_rex: ``--dns_records\.jsonl$``
   * path_suffix: ``dns_records``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``DNS_RECORDS``
   * normalize: ``ecs_normalize/windows/live_response/dns_records.vrl``

Description
-----------

Parse DNS\_records.txt from DFIR ORC (custom ps1 command)

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
