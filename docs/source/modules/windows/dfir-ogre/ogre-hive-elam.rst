ogre-hive-elam
==============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:hive_elam`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of reg\_keys - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-hives-registry-value:

.. list-table::
   :header-rows: 1

   * - registry.path
     - Relation
     - Message
   * - 
     - `registry-value <rel-windows-dfir-ogre-hives-registry-value_>`_
     - ``Registry value {registry.value} exists in key {registry.path}``

Relationships
-------------

.. _rel-windows-dfir-ogre-hives-registry-value:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `registry-value <tl-windows-dfir-ogre-hives-registry-value_>`_
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
   * - ``"Windows Registry"``
     - ``event.provider``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``name``
     - ``registry.value``
   * - ``type``
     - ``registry.data.type``
   * - ``data``
     - ``action.properties.value_data``
   * - ``parse_timestamp(mtime)``
     - ``registry.mtime``
   * - ``parse_timestamp(mtime)``
     - ``timestamp``
   * - ``to_int(size)``
     - ``action.properties.size``
   * - ``to_bool(is_placeholder)``
     - ``action.properties.is_placeholder``
   * - ``security_descriptor``
     - ``key_security``
