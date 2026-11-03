extract_orc
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``filesystem:ntfs:i30`` | name_rex: ``r"I30Info.*.csv$"``
   * ``filesystem:ntfs:info`` | name_rex: ``r"NTFSInfo.*.csv$"``
   * ``filesystem:ntfs:usn`` | name_rex: ``r"USNInfo.*.csv$"``
   * ``orc:collected_files`` | name_rex: ``r"GetThis.csv$"``
   * ``orc:files`` | name_rex: ``r"\.csv$"``
   * ``_json`` | name_rex: ``r"(?i)(?:^|/)processes(?:\d+|_[^/]+)?\.csv$"``
   * ``_json`` | name_rex: ``r"(?i)^systeminfo(?:_.+)?\.csv$"``
   * ``windows:sysinternals:autoruns`` | name_rex: ``r"autoruns.*csv$"``

Description
-----------

Used to execute internal pre-processing for DFIR-ORC capture

Timeline
--------

**``windows/live_response/systeminfo.yml``**

No timeline messages.

**``windows/live_response/ps1_processes.yml``**

No timeline messages.

**``windows/NTFSInfo.yml``**

No timeline messages.

**``windows/NTFSInfo_usn.yml``**

.. _tl-windows-NTFSInfo_usn-usn-record:

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

**``windows/NTFSInfo_i30.yml``**

No timeline messages.

**``windows/live_response/autoruns.yml``**

No timeline messages.

**``windows/collected_files.yml``**

.. _tl-windows-collected_files-collected:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `collected <rel-windows-collected_files-collected_>`_
     - ``File {file.path} was collected by DFIR-ORC (MD5 {hash.md5})``

Relationships
-------------

**``windows/live_response/systeminfo.yml``**

No relationships.

**``windows/live_response/ps1_processes.yml``**

No relationships.

**``windows/NTFSInfo.yml``**

No relationships.

**``windows/NTFSInfo_usn.yml``**

No relationships.

**``windows/NTFSInfo_i30.yml``**

No relationships.

**``windows/live_response/autoruns.yml``**

No relationships.

**``windows/collected_files.yml``**

.. _rel-windows-collected_files-collected:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `collected <tl-windows-collected_files-collected_>`_
     - ``file.path``
     - ``hash.md5``
     - ``collected as``

Fields
------

**``windows/live_response/systeminfo.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"systeminfo"``
     - ``event.action``
   * - ``"systeminfo"``
     - ``event.code``
   * - ``"Windows Systeminfo"``
     - ``event.provider``
   * - ``custom``
     - 

**``windows/live_response/ps1_processes.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows Process (generic)"``
     - ``event.provider``
   * - ``"process_snapshot"``
     - ``event.action``
   * - ``"process_snapshot"``
     - ``event.code``
   * - ``custom``
     - 
   * - ``to_string!(del(.WindowsVersion))``
     - ``host.os.version``
   * - ``to_string!(del(.OSName))``
     - ``host.os.full``
   * - ``custom``
     - 
   * - ``to_string!(del(.Product))``
     - ``action.properties.product``
   * - ``to_string!(del(.FileVersion))``
     - ``action.properties.file_version``
   * - ``to_string!(del(.ProductVersion))``
     - ``action.properties.product_version``
   * - ``to_string!(del(.CreationClassName))``
     - ``action.properties.creation_class_name``
   * - ``to_string!(del(.OSCreationClassName))``
     - ``action.properties.os_creation_class_name``
   * - ``custom``
     - 
   * - ``to_string!(del(.KernelModeTime))``
     - ``action.properties.kernel_mode_time_raw``
   * - ``to_string!(del(.UserModeTime))``
     - ``action.properties.user_mode_time_raw``
   * - ``to_string!(del(.TotalProcessorTime))``
     - ``action.properties.total_processor_time``
   * - ``to_string!(del(.UserProcessorTime))``
     - ``action.properties.user_processor_time``
   * - ``to_string!(del(.PrivilegedProcessorTime))``
     - ``action.properties.privileged_processor_time``
   * - ``custom``
     - 
   * - ``to_string!(del(.PriorityClass))``
     - ``action.properties.priority_class``
   * - ``to_string!(del(.HasExited))``
     - ``action.properties.has_exited_raw``
   * - ``custom``
     - 

**``windows/NTFSInfo.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"ntfs_file"``
     - ``event.action``
   * - ``"Windows NTFSInfo (detail)"``
     - ``event.provider``
   * - ``File``
     - ``file.name``
   * - ``to_int(SizeInBytes)``
     - ``file.size``
   * - ``Attributes``
     - ``file.attributes``
   * - ``Owner``
     - ``file.owner``
   * - ``ComputerName``
     - ``host.name``
   * - ``FullName``
     - ``file.path``
   * - ``parse_timestamp(CreationDate)``
     - ``file.created``
   * - ``parse_timestamp(LastModificationDate)``
     - ``file.mtime``
   * - ``parse_timestamp(LastAccessDate)``
     - ``file.accessed``
   * - ``parse_timestamp(LastAttrChangeDate)``
     - ``file.ctime``
   * - ``parse_timestamp(FileNameCreationDate)``
     - ``file.fn_created``
   * - ``parse_timestamp(FileNameLastModificationDate)``
     - ``file.fn_mtime``
   * - ``parse_timestamp(FileNameLastAccessDate)``
     - ``file.fn_accessed``
   * - ``parse_timestamp(FileNameLastAttrModificationDate)``
     - ``file.fn_ctime``
   * - ``MD5``
     - ``hash.md5``
   * - ``SHA1``
     - ``hash.sha1``
   * - ``SHA256``
     - ``hash.sha256``
   * - ``SSDeep``
     - ``hash.ssdeep``
   * - ``Version``
     - ``pe.file_version``
   * - ``CompanyName``
     - ``pe.company``
   * - ``ProductName``
     - ``pe.product``
   * - ``OriginalFileName``
     - ``pe.original_file_name``
   * - ``AuthenticodeSigner``
     - ``code_signature.subject_name``
   * - ``AuthenticodeCA``
     - ``code_signature.issuer_name``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``VolumeID``
     - ``action.properties.VolumeID``
   * - ``USN``
     - ``action.properties.USN``
   * - ``FRN``
     - ``action.properties.FRN``
   * - ``ParentFRN``
     - ``action.properties.ParentFRN``
   * - ``ExtendedAttribute``
     - ``action.properties.ExtendedAttribute``
   * - ``ADS``
     - ``action.properties.ADS``
   * - ``FilenameID``
     - ``action.properties.FilenameID``
   * - ``DataID``
     - ``action.properties.DataID``
   * - ``RecordInUse``
     - ``action.properties.RecordInUse``
   * - ``ShortName``
     - ``action.properties.ShortName``
   * - ``PeSHA1``
     - ``action.properties.PeSHA1``
   * - ``PeSHA256``
     - ``action.properties.PeSHA256``
   * - ``PeMD5``
     - ``action.properties.PeMD5``
   * - ``FirstBytes``
     - ``action.properties.FirstBytes``
   * - ``TLSH``
     - ``action.properties.TLSH``
   * - ``SignedHash``
     - ``action.properties.SignedHash``
   * - ``OwnerId``
     - ``action.properties.OwnerId``
   * - ``OwnerSid``
     - ``action.properties.OwnerSid``
   * - ``Platform``
     - ``action.properties.Platform``
   * - ``TimeStamp``
     - ``action.properties.TimeStamp``
   * - ``SubSystem``
     - ``action.properties.SubSystem``
   * - ``FileType``
     - ``action.properties.FileType``
   * - ``FileOS``
     - ``action.properties.FileOS``
   * - ``FilenameFlags``
     - ``action.properties.FilenameFlags``
   * - ``SecDescrID``
     - ``action.properties.SecDescrID``
   * - ``EASize``
     - ``action.properties.EASize``
   * - ``SecurityDirectory``
     - ``action.properties.SecurityDirectory``
   * - ``SecurityDirectorySize``
     - ``action.properties.SecurityDirectorySize``
   * - ``SecurityDirectorySignatureSize``
     - ``action.properties.SecurityDirectorySignatureSize``
   * - ``AuthenticodeStatus``
     - ``action.properties.AuthenticodeStatus``
   * - ``AuthenticodeSignerThumbprint``
     - ``action.properties.AuthenticodeSignerThumbprint``
   * - ``AuthenticodeCAThumbprint``
     - ``action.properties.AuthenticodeCAThumbprint``
   * - ``FilenameIndex``
     - ``action.properties.FilenameIndex``
   * - ``DataIndex``
     - ``action.properties.DataIndex``
   * - ``SnapshotID``
     - ``action.properties.SnapshotID``
   * - ``custom``
     - 

**``windows/NTFSInfo_usn.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows NTFS USN Journal (detail)"``
     - ``event.provider``
   * - ``File``
     - ``file.name``
   * - ``FullPath``
     - ``file.path``
   * - ``FileAttributes``
     - ``file.attributes``
   * - ``ComputerName``
     - ``host.name``
   * - ``USN``
     - ``action.properties.USN``
   * - ``FRN``
     - ``action.properties.FRN``
   * - ``ParentFRN``
     - ``action.properties.ParentFRN``
   * - ``VolumeID``
     - ``action.properties.VolumeID``
   * - ``SnapshotID``
     - ``action.properties.SnapshotID``
   * - ``parse_timestamp(TimeStamp)``
     - ``timestamp``
   * - ``downcase(Reason)``
     - ``event.action``
   * - ``Reason``
     - ``action.properties.Reason``

**``windows/NTFSInfo_i30.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"ntfs_filename"``
     - ``event.action``
   * - ``"Windows NTFS Filename (detail)"``
     - ``event.provider``
   * - ``Name``
     - ``file.name``
   * - ``to_int(DataSize)``
     - ``file.size``
   * - ``ComputerName``
     - ``host.name``
   * - ``parse_timestamp(FileNameCreationDate)``
     - ``file.fn_created``
   * - ``parse_timestamp(FileNameLastModificationDate)``
     - ``file.fn_mtime``
   * - ``parse_timestamp(FileNameLastAccessDate)``
     - ``file.fn_accessed``
   * - ``parse_timestamp(FileNameLastAttrModificationDate)``
     - ``file.fn_ctime``
   * - ``VolumeID``
     - ``action.properties.VolumeID``
   * - ``FRN``
     - ``action.properties.FRN``
   * - ``ParentFRN``
     - ``action.properties.ParentFRN``
   * - ``FilenameFlags``
     - ``action.properties.FilenameFlags``
   * - ``SnapshotID``
     - ``action.properties.SnapshotID``
   * - ``CarvedEntry``
     - ``action.properties.CarvedEntry``
   * - ``custom``
     - 

**``windows/live_response/autoruns.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.autoruns"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"autoruns_entry"``
     - ``event.action``
   * - ``"autoruns_entry"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows Autoruns CSV"``
     - ``event.provider``
   * - ``custom``
     - 

**``windows/collected_files.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"DFIR-ORC GetThis"``
     - ``event.provider``
   * - ``FullName``
     - ``file.path``
   * - ``to_int(SizeInBytes)``
     - ``file.size``
   * - ``ComputerName``
     - ``host.name``
   * - ``parse_timestamp(CreationDate)``
     - ``timestamp``
   * - ``parse_timestamp(CreationDate)``
     - ``file.created``
   * - ``parse_timestamp(LastModificationDate)``
     - ``file.mtime``
   * - ``parse_timestamp(LastAccessDate)``
     - ``file.accessed``
   * - ``parse_timestamp(LastAttrChangeDate)``
     - ``file.ctime``
   * - ``parse_timestamp(FileNameCreationDate)``
     - ``file.fn_created``
   * - ``parse_timestamp(FileNameLastModificationDate)``
     - ``file.fn_mtime``
   * - ``parse_timestamp(FileNameLastAccessDate)``
     - ``file.fn_accessed``
   * - ``parse_timestamp(FileNameLastAttrModificationDate)``
     - ``file.fn_ctime``
   * - ``MD5``
     - ``hash.md5``
   * - ``SHA1``
     - ``hash.sha1``
   * - ``SHA256``
     - ``hash.sha256``
   * - ``SSDeep``
     - ``hash.ssdeep``
   * - ``VolumeID``
     - ``action.properties.VolumeID``
   * - ``ParentFRN``
     - ``action.properties.ParentFRN``
   * - ``FRN``
     - ``action.properties.FRN``
   * - ``AttrType``
     - ``action.properties.AttrType``
   * - ``AttrName``
     - ``action.properties.AttrName``
   * - ``AttrID``
     - ``action.properties.AttrID``
   * - ``ContentType``
     - ``action.properties.ContentType``
   * - ``SnapshotID``
     - ``action.properties.SnapshotID``
   * - ``FindMatch``
     - ``action.properties.FindMatch``
   * - ``SampleName``
     - ``action.properties.SampleName``
   * - ``YaraRules``
     - ``action.properties.YaraRules``
   * - ``RecordInUse``
     - ``action.properties.RecordInUse``
   * - ``TLSH``
     - ``action.properties.TLSH``
   * - ``SampleCollectionDate``
     - ``action.properties.SampleCollectionDate``
