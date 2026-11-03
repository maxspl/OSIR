ogre-usn-info
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:filesystem:ntfs:usn`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of usninfo - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-usn_info-usn-record:

.. list-table::
   :header-rows: 1

   * - file.name
     - event.action
     - Relation
     - Message
   * - 
     - 
     - ``usn-record``
     - ``USN record for file {file.name}: {event.action}``

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
   * - ``"Windows NTFS USN Journal (detail)"``
     - ``event.provider``
   * - ``file``
     - ``file.name``
   * - ``file_path``
     - ``file.path``
   * - ``computer_name``
     - ``host.name``
   * - ``usn_number``
     - ``action.properties.usn_number``
   * - ``sequence_number``
     - ``action.properties.sequence_number``
   * - ``record_number``
     - ``action.properties.record_number``
   * - ``parent_sequence_number``
     - ``action.properties.parent_sequence_number``
   * - ``parent_record_number``
     - ``action.properties.parent_record_number``
   * - ``volume_id``
     - ``action.properties.volume_id``
   * - ``snapshot_id``
     - ``action.properties.snapshot_id``
   * - ``reason``
     - ``action.properties.reason``
   * - ``parse_timestamp(timestamp)``
     - ``timestamp``
   * - ``join(reason)``
     - ``event.action``
   * - ``downcase(event.action)``
     - ``event.action``
   * - ``custom``
     - 
