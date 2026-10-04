mongodb
=======

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``linux:app:mongodb`` | name_rex: ``r"mongod.log$"``

Description
-----------

Splunk logs ingestion of Mongodb logs.

Timeline
--------

No timeline messages.

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``get(.t, ["$date"]) ?? null``
     - ``timestamp``
   * - ``"fatal"``
     - ``event.severity``
   * - ``"error"``
     - ``event.severity``
   * - ``"warning"``
     - ``event.severity``
   * - ``"informational"``
     - ``event.severity``
   * - ``"debug " + string!(.s)``
     - ``event.severity``
   * - ``string!(.s)``
     - ``event.severity``
   * - ``to_string!(del(.c))``
     - ``event.kind``
   * - ``del(.id)``
     - ``event.id``
   * - ``to_string!(del(.ctx))``
     - ``event.context``
   * - ``to_string!(del(.svc))``
     - ``service.name``
   * - ``to_string!(del(.msg))``
     - ``message``
   * - ``del(.attr)``
     - ``log``
   * - ``custom``
     - 
   * - ``del(.tags)``
     - ``log.tags``
   * - ``del(.truncated)``
     - ``log.truncated``
   * - ``del(.size)``
     - ``log.size``
