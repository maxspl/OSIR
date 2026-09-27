extract_orc
===========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``filesystem:ntfs:i30`` | name_rex: ``I30Info.*.csv$``
   * ``filesystem:ntfs:info`` | name_rex: ``NTFSInfo.*.csv$``
   * ``filesystem:ntfs:usn`` | name_rex: ``USNInfo.*.csv$``
   * ``orc:collected_files`` | name_rex: ``GetThis.csv$``
   * ``orc:files`` | name_rex: ``\.csv$``
   * ``windows:autoruns`` | name_rex: ``autoruns.*csv$``
   * ``_json`` | name_rex: ``(?i)(?:^|/)processes(?:\d+|_[^/]+)?\.csv$``
   * ``_json`` | name_rex: ``(?i)^systeminfo(?:_.+)?\.csv$``

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

**``windows/NTFSInfo_i30.yml``**

No timeline messages.

**``windows/live_response/autoruns.yml``**

No timeline messages.

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
   * - ``"windows.systeminfo"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[host]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"systeminfo"``
     - ``event.action``
   * - ``"systeminfo"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
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
   * - ``"windows.process"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"Windows Process (generic)"``
     - ``event.provider``
   * - ``"state"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"process_snapshot"``
     - ``event.action``
   * - ``"process_snapshot"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``custom``
     - 
   * - ``to_string!(del(.WindowsVersion))``
     - ``host.os.version``
   * - ``to_string!(del(.OSName))``
     - ``host.os.full``
   * - ``custom``
     - 
   * - ``to_string!(del(.Product))``
     - ``process.Ext.snapshot.product``
   * - ``to_string!(del(.FileVersion))``
     - ``process.Ext.snapshot.file_version``
   * - ``to_string!(del(.ProductVersion))``
     - ``process.Ext.snapshot.product_version``
   * - ``to_string!(del(.CreationClassName))``
     - ``process.Ext.snapshot.creation_class_name``
   * - ``to_string!(del(.OSCreationClassName))``
     - ``process.Ext.snapshot.os_creation_class_name``
   * - ``custom``
     - 
   * - ``to_string!(del(.KernelModeTime))``
     - ``process.Ext.snapshot.kernel_mode_time_raw``
   * - ``to_string!(del(.UserModeTime))``
     - ``process.Ext.snapshot.user_mode_time_raw``
   * - ``to_string!(del(.TotalProcessorTime))``
     - ``process.Ext.snapshot.total_processor_time``
   * - ``to_string!(del(.UserProcessorTime))``
     - ``process.Ext.snapshot.user_processor_time``
   * - ``to_string!(del(.PrivilegedProcessorTime))``
     - ``process.Ext.snapshot.privileged_processor_time``
   * - ``custom``
     - 
   * - ``to_string!(del(.PriorityClass))``
     - ``process.Ext.snapshot.priority_class``
   * - ``to_string!(del(.HasExited))``
     - ``process.Ext.snapshot.has_exited_raw``
   * - ``custom``
     - 

**``windows/NTFSInfo.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.ntfsinfo"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"ntfs_file"``
     - ``event.action``
   * - ``"ntfs_file"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows NTFSInfo (detail)"``
     - ``event.provider``
   * - ``to_string!(del(.ComputerName))``
     - ``host.name``
   * - ``to_string!(del(.VolumeID))``
     - ``file.Ext.ntfs.volume_id``
   * - ``custom``
     - 

**``windows/NTFSInfo_i30.yml``**

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.ntfsinfo.filename"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"ntfs_filename"``
     - ``event.action``
   * - ``"ntfs_filename"``
     - ``event.code``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows NTFS Filename (detail)"``
     - ``event.provider``
   * - ``to_string!(del(.ComputerName))``
     - ``host.name``
   * - ``to_string!(del(.VolumeID))``
     - ``file.Ext.ntfs.volume_id``
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
