loki_uac
========

.. tip:: Ingestion into Splunk.

   **``loki:files``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``loki_uac``
   * sourcetype: ``loki:files``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Loki``
   * normalize: ``ecs_normalize/scan/loki.vrl``

Description
-----------

YARA/IOC scan of the files collected by UAC (output of the extract\_uac module) using Loki-RS.

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
