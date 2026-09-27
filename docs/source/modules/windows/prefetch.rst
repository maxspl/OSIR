prefetch
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:prefetch`` | name_rex: ``\.jsonl$``

Description
-----------

Eric Zimmerman - PECmd.exe

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"windows.prefetch"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[start, info]``
     - ``event.type``
   * - ``"prefetch_summary"``
     - ``event.action``
   * - ``"info"``
     - ``log.level``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
   * - ``to_string!(del(.Hash))``
     - ``prefetch.hash``
   * - ``to_string!(del(.Version))``
     - ``prefetch.version``
   * - ``custom``
     - 
   * - ``to_string!(del(.Volume0Name))``
     - ``prefetch.volume0_name``
   * - ``to_string!(del(.Volume0Serial))``
     - ``prefetch.volume0_serial``
   * - ``custom``
     - 
   * - ``to_string!(del(.Volume1Name))``
     - ``prefetch.volume1_name``
   * - ``to_string!(del(.Volume1Serial))``
     - ``prefetch.volume1_serial``
   * - ``custom``
     - 
   * - ``"success"``
     - ``event.outcome``
