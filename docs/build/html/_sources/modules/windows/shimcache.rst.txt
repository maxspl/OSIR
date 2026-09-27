shimcache
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:registry:hklm:shimcache`` | name_rex: ``\.csv$``

Description
-----------

Parsing of ShimCache artifact.

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
   * - ``"windows.shimcache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows ShimCache (AppCompatCache)"``
     - ``event.provider``
   * - ``"shimcache_entry"``
     - ``event.code``
   * - ``"shimcache_entry"``
     - ``event.action``
   * - ``custom``
     - 
   * - ``to_string!(del(.SourceFile))``
     - ``file.Ext.shimcache.source_file``
   * - ``custom``
     - 
