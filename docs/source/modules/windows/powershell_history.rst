powershell_history
==================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:powershell_history`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parse ConsoleHost\_history.txt

Timeline
--------

.. _tl-windows-powershell_history-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - ``executed``
     - ``PowerShell command was executed: {process.command_line}``

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``command``
     - ``process.command_line``
   * - ``to_int(line_number)``
     - ``event.sequence``
