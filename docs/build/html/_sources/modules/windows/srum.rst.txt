srum
====

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:srum`` | name_rex: ``--srum-.*\.jsonl$``

Description
-----------

Parsing of SRUM artifact.

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
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``custom``
     - 
   * - ``[info]``
     - ``event.type``
   * - ``[host]``
     - ``event.category``
   * - ``custom``
     - 
