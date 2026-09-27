mactime
=======

.. tip:: Ingestion into Splunk.

   **``linux:files:bodyfile``**

   * name_rex: ``bodyfile.*\.jsonl$``
   * sourcetype: ``linux:files:bodyfile``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``bodyfile``
   * normalize: ``ecs_normalize/linux/mactime.vrl``

Description
-----------

Parsing logs from '/bodyfile' in UAC collect

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
