win_handle
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:handle`` | name_rex: ``--win_handle\.jsonl$``

Description
-----------

Parse handle from DFIR ORC (handle.exe /a command)

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"windows.handle"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"handle_entry"``
     - ``event.action``
   * - ``custom``
     - 
