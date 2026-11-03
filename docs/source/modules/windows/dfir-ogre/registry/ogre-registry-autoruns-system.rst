ogre-registry-autoruns-system
=============================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:registry:autoruns_system`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of autorun\_hive - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-registry-autoruns-autoruns-key:

.. list-table::
   :header-rows: 1

   * - action.properties.type
     - Relation
     - Message
   * - 
     - ``autoruns-key``
     - ``Autoruns registry key {registry.path} of type {action.properties.type} exists``

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
   * - ``"Windows Autoruns (dfir-ogre)"``
     - ``event.provider``
   * - ``key_path``
     - ``registry.path``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(key_modif_time)``
     - ``timestamp``
   * - ``type``
     - ``action.properties.type``
   * - ``values``
     - ``action.properties.values``
   * - ``image_path``
     - ``action.properties.image_path``
   * - ``enabled``
     - ``action.properties.enabled``
