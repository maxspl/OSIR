amcache
=======

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:amcache`` | name_rex: ``\.csv$``

Description
-----------

Parsing of amcache artifact.

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
   * - ``to_string!(del(.FullPath))``
     - ``file.path``
   * - ``to_string!(del(.LnkName))``
     - ``file.path``
   * - ``to_string!(del(.KeyName))``
     - ``file.path``
   * - ``to_string!(del(.Directory))``
     - ``file.directory``
   * - ``to_string!(del(.Name))``
     - ``file.name``
   * - ``custom``
     - 
   * - ``to_string!(del(.LnkName))``
     - ``file.lnk_name``
   * - ``custom``
     - 
   * - ``to_string!(del(.ProductName))``
     - ``file.product``
   * - ``to_string!(del(.ProductVersion))``
     - ``file.product_version``
   * - ``to_string!(del(.Version))``
     - ``file.version``
   * - ``to_string!(del(.Description))``
     - ``file.description``
   * - ``to_string!(del(.Language))``
     - ``file.Ext.amcache.language``
   * - ``to_string!(del(.BinaryType))``
     - ``file.Ext.amcache.binary_type``
   * - ``to_string!(del(.BinFileVersion))``
     - ``file.Ext.amcache.bin_file_version``
   * - ``to_string!(del(.BinProductVersion))``
     - ``file.Ext.amcache.bin_product_version``
   * - ``custom``
     - 
   * - ``to_string!(del(.ApplicationName))``
     - ``file.Ext.amcache.application_name``
   * - ``to_string!(del(.ProgramId))``
     - ``file.Ext.amcache.program_id``
   * - ``to_string!(del(.LongPathHash))``
     - ``file.Ext.amcache.long_path_hash``
   * - ``custom``
     - 
   * - ``to_string!(del(.ModelName))``
     - ``device.model``
   * - ``to_string!(del(.ModelNumber))``
     - ``device.Ext.amcache.model_number``
   * - ``to_string!(del(.Manufacturer))``
     - ``device.manufacturer``
   * - ``custom``
     - 
   * - ``to_string!(del(.Categories))``
     - ``device.Ext.amcache.categories_raw``
   * - ``to_string!(del(.DiscoveryMethod))``
     - ``device.Ext.amcache.discovery_method``
   * - ``to_string!(del(.Icon))``
     - ``device.Ext.amcache.icon_resource``
   * - ``custom``
     - 
   * - ``to_string!(del(.ClassGuid))``
     - ``device.Ext.amcache.class_guid``
   * - ``to_string!(del(.BusReportedDescription))``
     - ``device.Ext.amcache.bus_reported_description``
   * - ``to_string!(del(.Enumerator))``
     - ``device.Ext.amcache.enumerator``
   * - ``to_string!(del(.HWID))``
     - ``device.Ext.amcache.hwid``
   * - ``to_string!(del(.ParentId))``
     - ``device.Ext.amcache.parent_id``
   * - ``to_string!(del(.Stackid))``
     - ``device.Ext.amcache.stack_id``
   * - ``custom``
     - 
   * - ``to_string!(del(.DriverName))``
     - ``file.Ext.amcache.driver.name``
   * - ``to_string!(del(.DriverCompany))``
     - ``file.Ext.amcache.driver.company``
   * - ``to_string!(del(.Product))``
     - ``file.product``
   * - ``to_string!(del(.DriverVersion))``
     - ``file.Ext.amcache.driver.version``
   * - ``to_string!(del(.DriverVerVersion))``
     - ``file.Ext.amcache.driver.version_string``
   * - ``to_string!(del(.WdfVersion))``
     - ``file.Ext.amcache.driver.wdf_version``
   * - ``to_string!(del(.DriverId))``
     - ``file.Ext.amcache.driver.id``
   * - ``to_string!(del(.DriverPackageStrongName))``
     - ``file.Ext.amcache.driver.package_strong_name``
   * - ``to_string!(del(.DriverType))``
     - ``file.Ext.amcache.driver.type``
   * - ``to_string!(del(.Inf))``
     - ``file.Ext.amcache.driver.inf``
   * - ``to_string!(del(.Service))``
     - ``file.Ext.amcache.driver.service``
   * - ``to_string!(del(.Provider))``
     - ``file.Ext.amcache.driver.provider``
   * - ``to_string!(del(.SubmissionId))``
     - ``file.Ext.amcache.driver_package_submission_id``
   * - ``to_string!(del(.Hwids))``
     - ``file.Ext.amcache.driver_package_hwids_raw``
   * - ``to_string!(del(.SYSFILE))``
     - ``file.Ext.amcache.driver_package_sysfile_raw``
   * - ``to_string!(del(.MatchingId))``
     - ``file.Ext.amcache.matching_id``
   * - ``custom``
     - 
   * - ``to_string!(del(.KeyLastWriteTimestamp))``
     - ``event.Ext.amcache.key_last_write_raw``
   * - ``to_string!(del(.FileKeyLastWriteTimestamp))``
     - ``event.Ext.amcache.file_key_last_write_raw``
   * - ``to_string!(del(.DriverLastWriteTime))``
     - ``event.Ext.amcache.driver_last_write_raw``
   * - ``to_string!(del(.DriverTimeStamp))``
     - ``event.Ext.amcache.driver_timestamp_raw``
   * - ``to_string!(del(.LinkDate))``
     - ``event.Ext.amcache.link_date_raw``
   * - ``to_string!(del(.Date))``
     - ``event.Ext.amcache.date_raw``
   * - ``to_string!(del(.DriverVerDate))``
     - ``event.Ext.amcache.driver_ver_date_raw``
   * - ``custom``
     - 
   * - ``"windows.amcache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"Windows Amcache (generic)"``
     - ``event.provider``
   * - ``"state"``
     - ``event.kind``
   * - ``[file]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
