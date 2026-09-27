hayabusa
========

.. tip:: Ingestion into Splunk.

   **``hayabusa``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``hayabusa``
   * sourcetype: ``hayabusa``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``hayabusa``
   * normalize: ``ecs_normalize/scan/hayabusa.vrl``

Description
-----------

Hayabusa scan of evtx files

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
