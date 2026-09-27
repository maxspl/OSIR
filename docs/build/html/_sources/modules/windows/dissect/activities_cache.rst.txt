activities_cache
================

.. tip:: Ingestion into Splunk.

   **``windows:activitiescache``**

   * name_rex: ``--activities_cache\.jsonl$``
   * host_rex: ``([\w\.-]+)--``
   * path_suffix: ``activities_cache``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``ActivitiesCache``
   * normalize: ``ecs_normalize/windows/activities_cache.vrl``

Description
-----------

Parse ActivitiesCache.db from DFIR ORC restore\_fs using Dissect plugin

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
