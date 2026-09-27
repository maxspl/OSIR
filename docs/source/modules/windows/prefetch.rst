prefetch
========

.. tip:: Ingestion into Splunk.

   **``windows:prefetch``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``prefetch``
   * sourcetype: ``windows:files:prefetch``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Prefetch``
   * normalize: ``ecs_normalize/windows/prefetch.vrl``

Description
-----------

Eric Zimmerman - PECmd.exe

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
