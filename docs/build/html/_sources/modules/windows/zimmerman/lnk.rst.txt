lnk
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:lnk`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of lnk artifact.

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
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows LNK"``
     - ``event.provider``
   * - ``"shortcut"``
     - ``event.action``
   * - ``"lnk"``
     - ``event.code``
   * - ``to_string!(del(.SourceFile))``
     - ``action.properties.source_file``
   * - ``to_string!(del(.ExtraBlocksPresent))``
     - ``action.properties.extra_blocks_present``
   * - ``to_string!(del(.HeaderFlags))``
     - ``action.properties.header_flags``
   * - ``to_string!(del(.FileAttributes))``
     - ``file.attributes``
   * - ``to_string!(del(.DriveType))``
     - ``action.properties.drive_type``
   * - ``to_string!(del(.VolumeSerialNumber))``
     - ``action.properties.volume_serial_number``
   * - ``to_string!(del(.VolumeLabel))``
     - ``action.properties.volume_label``
   * - ``custom``
     - 
   * - ``to_string!(del(.RelativePath))``
     - ``action.properties.relative_path``
   * - ``to_string!(del(.WorkingDirectory))``
     - ``action.properties.working_directory``
   * - ``to_string!(del(.Arguments))``
     - ``action.properties.arguments``
   * - ``custom``
     - 
   * - ``to_string!(del(.MACVendor))``
     - ``action.properties.mac_vendor``
   * - ``custom``
     - 
   * - ``to_string!(del(.TargetMFTEntryNumber))``
     - ``action.properties.target_mft_entry_number``
   * - ``to_string!(del(.TargetMFTSequenceNumber))``
     - ``action.properties.target_mft_sequence_number``
   * - ``custom``
     - 
