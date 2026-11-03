shimcache
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:shimcache`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of ShimCache artifact.

Timeline
--------

.. _tl-windows-zimmerman-shimcache-shimcache-entry:

.. list-table::
   :header-rows: 1

   * - file.path
     - Relation
     - Message
   * - 
     - `shimcache-entry <rel-windows-zimmerman-shimcache-shimcache-entry_>`_
     - ``ShimCache entry exists for {file.path}``

Relationships
-------------

.. _rel-windows-zimmerman-shimcache-shimcache-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `shimcache-entry <tl-windows-zimmerman-shimcache-shimcache-entry_>`_
     - ``file.path``
     - ``action.properties.Executed``
     - ``executed``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows AppCompatCache (ShimCache)"``
     - ``event.provider``
   * - ``Path``
     - ``file.path``
   * - ``parse_timestamp(LastModifiedTimeUTC)``
     - ``file.mtime``
   * - ``parse_timestamp(LastModifiedTimeUTC)``
     - ``timestamp``
   * - ``to_int(ControlSet)``
     - ``action.properties.ControlSet``
   * - ``to_int(CacheEntryPosition)``
     - ``action.properties.CacheEntryPosition``
   * - ``to_bool(Executed)``
     - ``action.properties.Executed``
   * - ``to_bool(Duplicate)``
     - ``action.properties.Duplicate``
   * - ``SourceFile``
     - ``action.properties.SourceFile``
