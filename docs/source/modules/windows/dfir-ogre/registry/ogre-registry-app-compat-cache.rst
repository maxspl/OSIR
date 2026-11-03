ogre-registry-app-compat-cache
==============================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:registry:app_compat_cache`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of app\_compat\_cache - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-registry-app_compat_cache-shimcache-entry:

.. list-table::
   :header-rows: 1

   * - file.path
     - Relation
     - Message
   * - 
     - ``shimcache-entry``
     - ``ShimCache entry exists for {file.path}``

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
   * - ``"Windows AppCompatCache (ShimCache)"``
     - ``event.provider``
   * - ``path``
     - ``file.path``
   * - ``split!(replace(to_string!(.path), pattern: "\\", with: "/"), "/")[-1]``
     - ``file.name``
   * - ``to_int(index)``
     - ``action.properties.index``
   * - ``replace(to_string!(.key_path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(modification_date)``
     - ``timestamp``
