IIS
===

.. tip:: Ingestion into Splunk.

   **``windows:iis``**

   * name_rex: ``--IIS\.jsonl$``
   * host_rex: ``([\w\.-]+)--``
   * path_suffix: ``IIS``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``IIS``
   * normalize: ``ecs_normalize/windows/iis.vrl``

Description
-----------

Parse IIS from DFIR ORC restore\_fs using Dissect plugin

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
