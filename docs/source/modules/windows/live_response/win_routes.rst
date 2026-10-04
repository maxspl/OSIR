win_routes
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:routes`` | name_rex: ``r"--win_routes\.jsonl$"``

Description
-----------

Parse routes.txt from DFIR ORC (route.exe PRINT command)

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
   * - ``custom``
     - 
   * - ``"windows.routes"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[network, configuration]``
     - ``event.category``
   * - ``[info, routing]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows routes"``
     - ``event.provider``
   * - ``"ipv4"``
     - ``network.type``
   * - ``"ip"``
     - ``network.protocol``
   * - ``custom``
     - 
