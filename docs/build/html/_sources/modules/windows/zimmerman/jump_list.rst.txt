jump_list
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:jumplist`` | name_rex: ``r"\.csv$"``

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
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows JumpList (generic)"``
     - ``event.provider``
   * - ``"jumplist"``
     - ``event.action``
   * - ``SourceFile``
     - ``action.properties.SourceFile``
   * - ``AppId``
     - ``action.properties.AppId``
   * - ``AppIdDescription``
     - ``action.properties.AppIdDescription``
   * - ``to_bool(HasSps)``
     - ``action.properties.HasSps``
   * - ``to_int(DestListVersion)``
     - ``action.properties.DestListVersion``
   * - ``to_int(LastUsedEntryNumber)``
     - ``action.properties.LastUsedEntryNumber``
   * - ``to_int(MRU)``
     - ``action.properties.MRU``
   * - ``to_int(InteractionCount)``
     - ``action.properties.InteractionCount``
   * - ``to_bool(PinStatus)``
     - ``action.properties.PinStatus``
   * - ``EntryName``
     - ``action.properties.EntryName``
   * - ``ExtraBlocksPresent``
     - ``action.properties.ExtraBlocksPresent``
   * - ``HeaderFlags``
     - ``action.properties.HeaderFlags``
   * - ``Arguments``
     - ``action.properties.Arguments``
   * - ``Notes``
     - ``action.properties.Notes``
   * - ``RelativePath``
     - ``action.properties.RelativePath``
   * - ``WorkingDirectory``
     - ``action.properties.WorkingDirectory``
   * - ``DriveType``
     - ``action.properties.DriveType``
   * - ``VolumeSerialNumber``
     - ``action.properties.VolumeSerialNumber``
   * - ``VolumeLabel``
     - ``action.properties.VolumeLabel``
   * - ``FileBirthDroid``
     - ``action.properties.FileBirthDroid``
   * - ``FileDroid``
     - ``action.properties.FileDroid``
   * - ``VolumeBirthDroid``
     - ``action.properties.VolumeBirthDroid``
   * - ``VolumeDroid``
     - ``action.properties.VolumeDroid``
   * - ``TargetMFTEntryNumber``
     - ``action.properties.TargetMFTEntryNumber``
   * - ``TargetMFTSequenceNumber``
     - ``action.properties.TargetMFTSequenceNumber``
   * - ``Path``
     - ``action.properties.Path``
   * - ``TargetIDAbsolutePath``
     - ``action.properties.TargetIDAbsolutePath``
   * - ``LocalPath``
     - ``action.properties.LocalPath``
   * - ``CommonPath``
     - ``action.properties.CommonPath``
   * - ``FileAttributes``
     - ``file.attributes``
   * - ``to_int(EntryNumber)``
     - ``event.sequence``
   * - ``Hostname``
     - ``host.name``
   * - ``MacAddress``
     - ``host.mac``
   * - ``MachineID``
     - ``host.id``
   * - ``MachineID``
     - ``host.name``
   * - ``MachineMACAddress``
     - ``host.mac``
   * - ``Path``
     - ``file.path``
   * - ``TargetIDAbsolutePath``
     - ``file.path``
   * - ``LocalPath``
     - ``file.path``
   * - ``CommonPath``
     - ``file.path``
   * - ``split!(to_string!(.file.path), "\\")[-1]``
     - ``file.name``
   * - ``to_int(FileSize)``
     - ``file.size``
   * - ``parse_timestamp(TargetCreated)``
     - ``file.created``
   * - ``parse_timestamp(TargetModified)``
     - ``file.mtime``
   * - ``parse_timestamp(TargetAccessed)``
     - ``file.accessed``
   * - ``parse_timestamp(SourceCreated)``
     - ``action.properties.SourceCreated``
   * - ``parse_timestamp(SourceModified)``
     - ``action.properties.SourceModified``
   * - ``parse_timestamp(SourceAccessed)``
     - ``action.properties.SourceAccessed``
   * - ``parse_timestamp(CreationTime)``
     - ``action.properties.CreationTime``
   * - ``parse_timestamp(LastModified)``
     - ``timestamp``
   * - ``parse_timestamp(LastModified)``
     - ``event.created``
   * - ``"jumplist.entry_last_modified"``
     - ``action.properties.timestamp_source``
   * - ``parse_timestamp(TargetCreated)``
     - ``action.properties.TargetCreated``
   * - ``parse_timestamp(TargetModified)``
     - ``action.properties.TargetModified``
   * - ``parse_timestamp(TargetAccessed)``
     - ``action.properties.TargetAccessed``
   * - ``parse_timestamp(TrackerCreatedOn)``
     - ``action.properties.TrackerCreatedOn``
