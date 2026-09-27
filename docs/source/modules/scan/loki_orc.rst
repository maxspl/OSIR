loki_orc
========

.. tip:: Ingestion into Splunk.

   **``loki:files``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``loki_orc``
   * sourcetype: ``loki:files``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Loki``
   * normalize: ``ecs_normalize/scan/loki.vrl``

Description
-----------

YARA/IOC scan of the filesystem rebuilt from a DFIR ORC collection (output of the restore\_fs module) using Loki-RS.

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
