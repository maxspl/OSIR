ogre-recycle-bin
================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:recycle_bin`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of recycle\_bin - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-recycle_bin-deleted:

.. list-table::
   :header-rows: 1

   * - file.path
     - Relation
     - Message
   * - 
     - ``deleted``
     - ``File {file.path} was deleted``

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
   * - ``"Windows Recycle Bin"``
     - ``event.provider``
   * - ``path``
     - ``file.path``
   * - ``to_int(size)``
     - ``file.size``
   * - ``to_int(header)``
     - ``action.properties.header``
   * - ``parse_timestamp(uninstall_date)``
     - ``timestamp``
   * - ``custom``
     - 
