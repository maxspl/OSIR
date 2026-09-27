lnk
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:lnk`` | name_rex: ``\.csv$``

Description
-----------

Parsing of lnk artifact.

Timeline
--------

No timeline messages.

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
   * - ``"windows.lnk"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"Windows LNK"``
     - ``event.provider``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"shortcut"``
     - ``event.action``
   * - ``"lnk"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``to_string!(del(.SourceFile))``
     - ``file.Ext.lnk.source_file``
   * - ``to_string!(del(.ExtraBlocksPresent))``
     - ``file.Ext.lnk.extra_blocks_present``
   * - ``to_string!(del(.HeaderFlags))``
     - ``file.Ext.lnk.header_flags``
   * - ``to_string!(del(.FileAttributes))``
     - ``file.attributes``
   * - ``to_string!(del(.DriveType))``
     - ``file.Ext.lnk.drive_type``
   * - ``to_string!(del(.VolumeSerialNumber))``
     - ``file.Ext.lnk.volume_serial_number``
   * - ``to_string!(del(.VolumeLabel))``
     - ``file.Ext.lnk.volume_label``
   * - ``custom``
     - 
   * - ``to_string!(del(.RelativePath))``
     - ``file.Ext.lnk.relative_path``
   * - ``to_string!(del(.WorkingDirectory))``
     - ``file.Ext.lnk.working_directory``
   * - ``to_string!(del(.Arguments))``
     - ``file.Ext.lnk.arguments``
   * - ``custom``
     - 
   * - ``to_string!(del(.MACVendor))``
     - ``host.Ext.lnk.mac_vendor``
   * - ``custom``
     - 
   * - ``to_string!(del(.TargetMFTEntryNumber))``
     - ``file.Ext.lnk.target_mft_entry_number``
   * - ``to_string!(del(.TargetMFTSequenceNumber))``
     - ``file.Ext.lnk.target_mft_sequence_number``
   * - ``custom``
     - 
