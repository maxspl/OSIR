win_netstat
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:netstat`` | name_rex: ``r"--win_netstat\.jsonl$"``

Description
-----------

Parse netstat.txt from DFIR ORC (netstat.exe -a -n -o command)

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
   * - ``encode_json(.)``
     - ``event.original``
   * - ``"windows.netstat"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[network]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``custom``
     - 
