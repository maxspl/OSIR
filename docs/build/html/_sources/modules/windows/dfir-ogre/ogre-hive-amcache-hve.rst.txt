ogre-hive-amcache-hve
=====================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:hive_amcache_hve`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of reg\_keys - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-amcache-file-entry:
.. _tl-windows-amcache-device-connected:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `file-entry <rel-windows-amcache-file-entry_>`_
     - ``Amcache file entry exists for {file.path} (SHA1 {file.hash.sha1})``
   * - ``device-connected``
     - ``Device {labels.friendly_name} was connected``

Relationships
-------------

.. _rel-windows-amcache-file-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `file-entry <tl-windows-amcache-file-entry_>`_
     - ``file.path``
     - ``file.hash.sha1``
     - ``hashed as``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.amcache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[file, driver, device]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows AmCache"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``parse_timestamp(FileKeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(FileKeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``FullPath``
     - ``file.path``
   * - ``Name``
     - ``file.name``
   * - ``to_int(Size)``
     - ``file.size``
   * - ``FileExtension``
     - ``file.extension``
   * - ``SHA1``
     - ``file.hash.sha1``
   * - ``Description``
     - ``file.description``
   * - ``Version``
     - ``file.version``
   * - ``parse_timestamp(LinkDate)``
     - ``file.mtime``
   * - ``ApplicationName``
     - ``labels.application_name``
   * - ``ProgramId``
     - ``labels.program_id``
   * - ``to_bool(IsOsComponent)``
     - ``labels.is_os_component``
   * - ``to_bool(IsPeFile)``
     - ``labels.is_pe_file``
   * - ``BinaryType``
     - ``labels.binary_type``
   * - ``ProductName``
     - ``labels.product_name``
   * - ``ProductVersion``
     - ``labels.product_version``
   * - ``BinFileVersion``
     - ``labels.bin_file_version``
   * - ``BinProductVersion``
     - ``labels.bin_product_version``
   * - ``LongPathHash``
     - ``labels.long_path_hash``
   * - ``to_int(Usn)``
     - ``labels.usn``
   * - ``Language``
     - ``labels.language``
   * - ``OriginalFileName``
     - ``labels.original_file_name``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``labels.key_name``
   * - ``Manufacturer``
     - ``device.manufacturer``
   * - ``ModelName``
     - ``device.model.name``
   * - ``ModelNumber``
     - ``labels.model_number``
   * - ``ModelId``
     - ``labels.model_id``
   * - ``FriendlyName``
     - ``labels.friendly_name``
   * - ``Categories``
     - ``labels.categories``
   * - ``PrimaryCategory``
     - ``labels.primary_category``
   * - ``DiscoveryMethod``
     - ``labels.discovery_method``
   * - ``Icon``
     - ``labels.icon``
   * - ``to_bool(IsActive)``
     - ``labels.is_active``
   * - ``to_bool(IsConnected)``
     - ``labels.is_connected``
   * - ``to_bool(IsMachineContainer)``
     - ``labels.is_machine_container``
   * - ``to_bool(IsNetworked)``
     - ``labels.is_networked``
   * - ``to_bool(IsPaired)``
     - ``labels.is_paired``
   * - ``to_int(State)``
     - ``labels.state``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``labels.key_name``
   * - ``BusReportedDescription``
     - ``labels.bus_reported_description``
   * - ``Class``
     - ``labels.class``
   * - ``ClassGuid``
     - ``labels.class_guid``
   * - ``Compid``
     - ``labels.compid``
   * - ``ContainerId``
     - ``labels.container_id``
   * - ``Description``
     - ``labels.description``
   * - ``DriverId``
     - ``labels.driver_id``
   * - ``DriverName``
     - ``labels.driver_name``
   * - ``parse_timestamp(DriverVerDate)``
     - ``labels.driver_ver_date``
   * - ``DriverVerVersion``
     - ``labels.driver_ver_version``
   * - ``Enumerator``
     - ``labels.enumerator``
   * - ``HWID``
     - ``labels.hwid``
   * - ``Inf``
     - ``labels.inf``
   * - ``to_int(InstallState)``
     - ``labels.install_state``
   * - ``Manufacturer``
     - ``labels.manufacturer``
   * - ``MatchingId``
     - ``labels.matching_id``
   * - ``Model``
     - ``labels.model``
   * - ``ParentId``
     - ``labels.parent_id``
   * - ``to_int(ProblemCode)``
     - ``labels.problem_code``
   * - ``Provider``
     - ``labels.provider``
   * - ``Service``
     - ``labels.service``
   * - ``Stackid``
     - ``labels.stackid``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``labels.key_name``
   * - ``parse_timestamp(DriverTimeStamp)``
     - ``labels.driver_time_stamp``
   * - ``parse_timestamp(DriverLastWriteTime)``
     - ``labels.driver_last_write_time``
   * - ``DriverName``
     - ``labels.driver_name``
   * - ``to_bool(DriverInBox)``
     - ``labels.driver_in_box``
   * - ``to_bool(DriverIsKernelMode)``
     - ``labels.driver_is_kernel_mode``
   * - ``to_bool(DriverSigned)``
     - ``labels.driver_signed``
   * - ``DriverCheckSum``
     - ``labels.driver_check_sum``
   * - ``DriverCompany``
     - ``labels.driver_company``
   * - ``DriverId``
     - ``labels.driver_id``
   * - ``DriverPackageStrongName``
     - ``labels.driver_package_strong_name``
   * - ``DriverType``
     - ``labels.driver_type``
   * - ``DriverVersion``
     - ``labels.driver_version``
   * - ``to_int(ImageSize)``
     - ``labels.image_size``
   * - ``Inf``
     - ``labels.inf``
   * - ``Product``
     - ``labels.product``
   * - ``ProductVersion``
     - ``labels.product_version``
   * - ``Service``
     - ``labels.service``
   * - ``WdfVersion``
     - ``labels.wdf_version``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``labels.key_name``
   * - ``parse_timestamp(Date)``
     - ``labels.date``
   * - ``Class``
     - ``labels.class``
   * - ``Directory``
     - ``labels.directory``
   * - ``to_bool(DriverInBox)``
     - ``labels.driver_in_box``
   * - ``Hwids``
     - ``labels.hwids``
   * - ``Inf``
     - ``labels.inf``
   * - ``Provider``
     - ``labels.provider``
   * - ``SubmissionId``
     - ``labels.submission_id``
   * - ``SYSFILE``
     - ``labels.sysfile``
   * - ``Version``
     - ``labels.version``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``labels.key_name``
   * - ``LnkName``
     - ``file.path``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``name``
     - ``registry.value``
   * - ``type``
     - ``registry.data.type``
   * - ``data``
     - ``labels.value_data``
   * - ``parse_timestamp(mtime)``
     - ``timestamp``
   * - ``parse_timestamp(mtime)``
     - ``registry.mtime``
   * - ``to_int(size)``
     - ``labels.value_size``
   * - ``to_bool(is_placeholder)``
     - ``labels.is_placeholder``
   * - ``ogre_md``
     - ``labels.ogre_md``
