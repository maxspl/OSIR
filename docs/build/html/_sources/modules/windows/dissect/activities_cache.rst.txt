activities_cache
================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:activitiescache`` | name_rex: ``--activities_cache\.jsonl$``

Description
-----------

Parse ActivitiesCache.db from DFIR ORC restore\_fs using Dissect plugin

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``custom``
     - 
   * - ``"windows.activities_cache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[session]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows ActivitiesCache"``
     - ``event.provider``
   * - ``custom``
     - 
