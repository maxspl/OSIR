recycle_bin
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:recycle_bin`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of recycle bin artifact.

Timeline
--------

.. _tl-windows-zimmerman-recycle_bin-deleted:

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
   * - ``parse_timestamp(DeletedOn)``
     - ``timestamp``
   * - ``FileName``
     - ``file.path``
   * - ``to_int(FileSize)``
     - ``file.size``
   * - ``FileType``
     - ``action.properties.FileType``
   * - ``SourceName``
     - ``action.properties.SourceName``
   * - ``custom``
     - 
