ogre-hive-sam
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:hive_sam`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of reg\_keys - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-hives-registry-value:

.. list-table::
   :header-rows: 1

   * - registry.path
     - Relation
     - Message
   * - 
     - `registry-value <rel-windows-hives-registry-value_>`_
     - ``Registry value {registry.value} exists in key {registry.path}``

Relationships
-------------

.. _rel-windows-hives-registry-value:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `registry-value <tl-windows-hives-registry-value_>`_
     - ``registry.path``
     - ``registry.value``
     - ``contains``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.registry"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[registry]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows Registry"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``KeyPath``
     - ``registry.path``
   * - ``ValueName``
     - ``registry.value``
   * - ``ValueType``
     - ``registry.data.type``
   * - ``HiveType``
     - ``registry.hive``
   * - ``HivePath``
     - ``labels.hive_path``
   * - ``Description``
     - ``labels.description``
   * - ``Category``
     - ``labels.category``
   * - ``Comment``
     - ``labels.comment``
   * - ``ValueData``
     - ``labels.value_data``
   * - ``ValueData2``
     - ``labels.value_data2``
   * - ``ValueData3``
     - ``labels.value_data3``
   * - ``to_bool(Recursive)``
     - ``labels.recursive``
   * - ``to_bool(Deleted)``
     - ``labels.deleted``
   * - ``PluginDetailFile``
     - ``labels.plugin_detail_file``
   * - ``parse_timestamp(LastWriteTimestamp)``
     - ``timestamp``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``name``
     - ``registry.value``
   * - ``type``
     - ``registry.data.type``
   * - ``data``
     - ``labels.value_data``
   * - ``parse_timestamp(mtime)``
     - ``registry.mtime``
   * - ``parse_timestamp(mtime)``
     - ``timestamp``
   * - ``to_int(size)``
     - ``labels.value_size``
   * - ``to_bool(is_placeholder)``
     - ``labels.is_placeholder``
   * - ``security_descriptor``
     - ``labels.security_descriptor``
   * - ``ogre_md``
     - ``labels.ogre_md``
