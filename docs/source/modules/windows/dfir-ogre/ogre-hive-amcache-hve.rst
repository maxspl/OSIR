ogre-hive-amcache-hve
=====================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:hive_amcache_hve`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of reg\_keys - using ANSSI DFIR OGRE

Timeline
--------

No timeline messages.

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
   * - ``"Windows AmCache"``
     - ``event.provider``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``name``
     - ``registry.value``
   * - ``type``
     - ``registry.data.type``
   * - ``data``
     - ``action.properties.data``
   * - ``parse_timestamp(mtime)``
     - ``timestamp``
   * - ``parse_timestamp(mtime)``
     - ``registry.mtime``
   * - ``to_int(size)``
     - ``action.properties.size``
   * - ``to_bool(is_placeholder)``
     - ``action.properties.is_placeholder``
