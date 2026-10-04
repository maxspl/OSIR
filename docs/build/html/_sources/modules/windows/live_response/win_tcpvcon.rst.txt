win_tcpvcon
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:win_tcpvcon`` | name_rex: ``r"--win_tcpvcon\.jsonl$"``

Description
-----------

Parse routes.txt from DFIR ORC (Tcpvcon.exe -a -n -c command)

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
   * - ``"windows.tcpvcon"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[network]``
     - ``event.category``
   * - ``[info, connection]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Sysinternals Tcpvcon"``
     - ``event.provider``
   * - ``"ip"``
     - ``network.protocol``
   * - ``custom``
     - 
   * - ``to_string!(del(.process_name))``
     - ``process.name``
   * - ``custom``
     - 
