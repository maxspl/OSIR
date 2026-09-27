powershell_history
==================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:powershell_history`` | name_rex: ``\.jsonl$``

Description
-----------

Parse ConsoleHost\_history.txt

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.powershell_history"``
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
   * - ``"PowerShell History"``
     - ``event.provider``
   * - ``custom``
     - 
