jump_list
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:jumplist`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of jump list artifact.

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
   * - ``"windows.jumplist"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"Windows JumpList (generic)"``
     - ``event.provider``
   * - ``"state"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"jumplist"``
     - ``event.action``
   * - ``"jumplist"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``to_string!(del(.SourceFile))``
     - ``event.Ext.jumplist.source_file``
   * - ``to_string!(del(.HasSps))``
     - ``event.Ext.jumplist.has_sps``
   * - ``custom``
     - 
   * - ``to_string!(del(.ExtraBlocksPresent))``
     - ``event.Ext.jumplist.extra_blocks_present``
   * - ``to_string!(del(.HeaderFlags))``
     - ``event.Ext.jumplist.header_flags``
   * - ``to_string!(del(.FileAttributes))``
     - ``file.attributes``
   * - ``to_string!(del(.AppId))``
     - ``event.Ext.jumplist.app_id``
   * - ``to_string!(del(.AppIdDescription))``
     - ``event.Ext.jumplist.app_description``
   * - ``to_string!(del(.EntryName))``
     - ``event.Ext.jumplist.entry_name``
   * - ``custom``
     - 
   * - ``to_string!(del(.Notes))``
     - ``event.Ext.jumplist.notes``
   * - ``custom``
     - 
   * - ``to_string!(del(.RelativePath))``
     - ``file.Ext.jumplist.relative_path``
   * - ``to_string!(del(.WorkingDirectory))``
     - ``file.Ext.jumplist.working_directory``
   * - ``to_string!(del(.Arguments))``
     - ``file.Ext.jumplist.arguments``
   * - ``custom``
     - 
   * - ``to_string!(del(.DriveType))``
     - ``file.Ext.jumplist.drive_type``
   * - ``to_string!(del(.VolumeSerialNumber))``
     - ``file.Ext.jumplist.volume_serial_number``
   * - ``to_string!(del(.VolumeLabel))``
     - ``file.Ext.jumplist.volume_label``
   * - ``to_string!(del(.FileBirthDroid))``
     - ``file.Ext.jumplist.file_birth_droid``
   * - ``to_string!(del(.FileDroid))``
     - ``file.Ext.jumplist.file_droid``
   * - ``to_string!(del(.VolumeBirthDroid))``
     - ``file.Ext.jumplist.volume_birth_droid``
   * - ``to_string!(del(.VolumeDroid))``
     - ``file.Ext.jumplist.volume_droid``
   * - ``to_string!(del(.TargetMFTEntryNumber))``
     - ``file.Ext.jumplist.target_mft_entry_number``
   * - ``to_string!(del(.TargetMFTSequenceNumber))``
     - ``file.Ext.jumplist.target_mft_sequence_number``
   * - ``custom``
     - 
