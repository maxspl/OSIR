shimcache
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:registry:hklm:shimcache`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of ShimCache artifact.

Timeline
--------

.. _tl-windows-shimcache-shimcache-entry:

.. list-table::
   :header-rows: 1

   * - file.path
     - Relation
     - Message
   * - 
     - `shimcache-entry <rel-windows-shimcache-shimcache-entry_>`_
     - ``ShimCache entry exists for {file.path}``

Relationships
-------------

.. _rel-windows-shimcache-shimcache-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `shimcache-entry <tl-windows-shimcache-shimcache-entry_>`_
     - ``file.path``
     - ``labels.executed``
     - ``executed``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.shimcache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows AppCompatCache (ShimCache)"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``Path``
     - ``file.path``
   * - ``parse_timestamp(LastModifiedTimeUTC)``
     - ``file.mtime``
   * - ``parse_timestamp(LastModifiedTimeUTC)``
     - ``timestamp``
   * - ``to_int(ControlSet)``
     - ``labels.control_set``
   * - ``to_int(CacheEntryPosition)``
     - ``labels.cache_entry_position``
   * - ``to_bool(Executed)``
     - ``labels.executed``
   * - ``to_bool(Duplicate)``
     - ``labels.duplicate``
   * - ``SourceFile``
     - ``labels.source_file``
