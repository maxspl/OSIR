thor_lite_orc
=============

.. tip:: Ingestion into Splunk.

   **``thor:files``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``thor_lite_orc``
   * sourcetype: ``thor:files``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Thor``
   * normalize: ``ecs_normalize/scan/thor.vrl``

Description
-----------

Scan of collected file using Thor Lite.

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
