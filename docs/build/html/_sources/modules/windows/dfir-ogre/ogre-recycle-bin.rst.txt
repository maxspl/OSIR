ogre-recycle-bin
================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:recycle_bin`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of recycle\_bin - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-recycle_bin-deleted:

.. list-table::
   :header-rows: 1

   * - file.path
     - Relation
     - Message
   * - 
     - ``deleted``
     - ``File {file.path} was deleted on {timestamp}``

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
   * - ``"windows.recycle_bin"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[deletion]``
     - ``event.type``
   * - ``"Windows Recycle Bin"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``parse_timestamp(DeletedOn)``
     - ``timestamp``
   * - ``FileName``
     - ``file.path``
   * - ``to_int(FileSize)``
     - ``file.size``
   * - ``FileType``
     - ``labels.file_type``
   * - ``SourceName``
     - ``labels.source_name``
   * - ``path``
     - ``file.path``
   * - ``to_int(size)``
     - ``file.size``
   * - ``to_int(header)``
     - ``labels.header``
   * - ``parse_timestamp(uninstall_date)``
     - ``timestamp``
   * - ``ogre_md``
     - ``labels.ogre_md``
