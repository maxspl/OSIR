ogre-vss-snapshot
=================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:vss_snapshot`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of vss\_snapshot - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-vss_snapshot-vss-snapshot:

.. list-table::
   :header-rows: 1

   * - action.properties.snapshot_id
     - Relation
     - Message
   * - 
     - `vss-snapshot <rel-windows-dfir-ogre-vss_snapshot-vss-snapshot_>`_
     - ``VSS snapshot {action.properties.snapshot_id} exists on volume {action.properties.volume_name}``

Relationships
-------------

.. _rel-windows-dfir-ogre-vss_snapshot-vss-snapshot:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `vss-snapshot <tl-windows-dfir-ogre-vss_snapshot-vss-snapshot_>`_
     - ``host.name``
     - ``action.properties.snapshot_id``
     - ``has snapshot``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows Volume Shadow Copy Service (VSS)"``
     - ``event.provider``
   * - ``snapshot_id``
     - ``action.properties.snapshot_id``
   * - ``volume_name``
     - ``action.properties.volume_name``
   * - ``device_instance``
     - ``action.properties.device_instance``
   * - ``attributes``
     - ``action.properties.attributes``
   * - ``parse_timestamp(creation_time)``
     - ``timestamp``
   * - ``custom``
     - 
