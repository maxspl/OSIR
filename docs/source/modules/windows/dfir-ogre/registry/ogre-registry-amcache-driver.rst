ogre-registry-amcache-driver
============================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:registry:amcache_driver`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of amcache\_driver - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-registry-registry-registry-key:

.. list-table::
   :header-rows: 1

   * - registry.path
     - Relation
     - Message
   * - 
     - ``registry-key``
     - ``Registry key {registry.path} exists``

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
   * - ``sha1``
     - ``hash.sha1``
   * - ``custom``
     - 
   * - ``"Windows Registry"``
     - ``event.provider``
   * - ``replace(to_string!(.key_path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``parse_timestamp(key_modif_time)``
     - ``timestamp``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``custom``
     - 
