win_listdlls
============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:dll`` | name_rex: ``r"--win_listdlls\.jsonl$"``

Description
-----------

Parse Listdlls.txt from DFIR ORC (Listdlls.exe command)

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
   * - ``"windows.listdlls"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Sysinternals ListDLLs"``
     - ``event.provider``
   * - ``custom``
     - 
   * - ``del(.process_name)``
     - ``process.name``
   * - ``custom``
     - 
   * - ``to_string!(del(.base_address))``
     - ``dll.Ext.base_address``
   * - ``custom``
     - 
