thor_orc_ram
============

.. tip:: Ingestion into Splunk.

   **``thor:memory``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``thor_orc_ram``
   * sourcetype: ``thor:memory``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Thor``
   * normalize: ``ecs_normalize/scan/thor.vrl``

Description
-----------

Scan of RAM restored file system from MemProcFS using Thor (requires Forensic license).

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
