win_bits
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:bits`` | name_rex: ``--win_bits\.jsonl$``

Description
-----------

Parse BITS\_jobs.txt from DFIR ORC (bitsadmin.exe /list /allusers /verbose command)

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
