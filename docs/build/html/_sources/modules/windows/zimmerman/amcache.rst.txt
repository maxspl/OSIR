amcache
=======

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:amcache`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of amcache artifact.

Timeline
--------

.. _tl-windows-zimmerman-amcache-file-entry:
.. _tl-windows-zimmerman-amcache-device-connected:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `file-entry <rel-windows-zimmerman-amcache-file-entry_>`_
     - ``Amcache file entry exists for {file.path} (SHA1 {hash.sha1})``
   * - ``device-connected``
     - ``Device {action.properties.FriendlyName} was connected``

Relationships
-------------

.. _rel-windows-zimmerman-amcache-file-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `file-entry <tl-windows-zimmerman-amcache-file-entry_>`_
     - ``file.path``
     - ``hash.sha1``
     - ``hashed as``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows AmCache"``
     - ``event.provider``
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
     - ``hash.sha1``
   * - ``Description``
     - ``file.description``
   * - ``Version``
     - ``file.version``
   * - ``parse_timestamp(LinkDate)``
     - ``file.mtime``
   * - ``ApplicationName``
     - ``action.properties.ApplicationName``
   * - ``ProgramId``
     - ``action.properties.ProgramId``
   * - ``to_bool(IsOsComponent)``
     - ``action.properties.IsOsComponent``
   * - ``to_bool(IsPeFile)``
     - ``action.properties.IsPeFile``
   * - ``BinaryType``
     - ``action.properties.BinaryType``
   * - ``ProductName``
     - ``action.properties.ProductName``
   * - ``ProductVersion``
     - ``action.properties.ProductVersion``
   * - ``BinFileVersion``
     - ``action.properties.BinFileVersion``
   * - ``BinProductVersion``
     - ``action.properties.BinProductVersion``
   * - ``LongPathHash``
     - ``action.properties.LongPathHash``
   * - ``to_int(Usn)``
     - ``action.properties.Usn``
   * - ``Language``
     - ``action.properties.Language``
   * - ``OriginalFileName``
     - ``action.properties.OriginalFileName``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``action.properties.KeyName``
   * - ``Manufacturer``
     - ``device.manufacturer``
   * - ``ModelName``
     - ``device.model.name``
   * - ``ModelNumber``
     - ``action.properties.ModelNumber``
   * - ``ModelId``
     - ``action.properties.ModelId``
   * - ``FriendlyName``
     - ``action.properties.FriendlyName``
   * - ``Categories``
     - ``action.properties.Categories``
   * - ``PrimaryCategory``
     - ``action.properties.PrimaryCategory``
   * - ``DiscoveryMethod``
     - ``action.properties.DiscoveryMethod``
   * - ``Icon``
     - ``action.properties.Icon``
   * - ``to_bool(IsActive)``
     - ``action.properties.IsActive``
   * - ``to_bool(IsConnected)``
     - ``action.properties.IsConnected``
   * - ``to_bool(IsMachineContainer)``
     - ``action.properties.IsMachineContainer``
   * - ``to_bool(IsNetworked)``
     - ``action.properties.IsNetworked``
   * - ``to_bool(IsPaired)``
     - ``action.properties.IsPaired``
   * - ``to_int(State)``
     - ``action.properties.State``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``action.properties.KeyName``
   * - ``BusReportedDescription``
     - ``action.properties.BusReportedDescription``
   * - ``Class``
     - ``action.properties.Class``
   * - ``ClassGuid``
     - ``action.properties.ClassGuid``
   * - ``Compid``
     - ``action.properties.Compid``
   * - ``ContainerId``
     - ``action.properties.ContainerId``
   * - ``Description``
     - ``action.properties.Description``
   * - ``DriverId``
     - ``action.properties.DriverId``
   * - ``DriverName``
     - ``action.properties.DriverName``
   * - ``parse_timestamp(DriverVerDate)``
     - ``action.properties.DriverVerDate``
   * - ``DriverVerVersion``
     - ``action.properties.DriverVerVersion``
   * - ``Enumerator``
     - ``action.properties.Enumerator``
   * - ``HWID``
     - ``action.properties.HWID``
   * - ``Inf``
     - ``action.properties.Inf``
   * - ``to_int(InstallState)``
     - ``action.properties.InstallState``
   * - ``Manufacturer``
     - ``action.properties.Manufacturer``
   * - ``MatchingId``
     - ``action.properties.MatchingId``
   * - ``Model``
     - ``action.properties.Model``
   * - ``ParentId``
     - ``action.properties.ParentId``
   * - ``to_int(ProblemCode)``
     - ``action.properties.ProblemCode``
   * - ``Provider``
     - ``action.properties.Provider``
   * - ``Service``
     - ``action.properties.Service``
   * - ``Stackid``
     - ``action.properties.Stackid``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``action.properties.KeyName``
   * - ``parse_timestamp(DriverTimeStamp)``
     - ``action.properties.DriverTimeStamp``
   * - ``parse_timestamp(DriverLastWriteTime)``
     - ``action.properties.DriverLastWriteTime``
   * - ``DriverName``
     - ``action.properties.DriverName``
   * - ``to_bool(DriverInBox)``
     - ``action.properties.DriverInBox``
   * - ``to_bool(DriverIsKernelMode)``
     - ``action.properties.DriverIsKernelMode``
   * - ``to_bool(DriverSigned)``
     - ``action.properties.DriverSigned``
   * - ``DriverCheckSum``
     - ``action.properties.DriverCheckSum``
   * - ``DriverCompany``
     - ``action.properties.DriverCompany``
   * - ``DriverId``
     - ``action.properties.DriverId``
   * - ``DriverPackageStrongName``
     - ``action.properties.DriverPackageStrongName``
   * - ``DriverType``
     - ``action.properties.DriverType``
   * - ``DriverVersion``
     - ``action.properties.DriverVersion``
   * - ``to_int(ImageSize)``
     - ``action.properties.ImageSize``
   * - ``Inf``
     - ``action.properties.Inf``
   * - ``Product``
     - ``action.properties.Product``
   * - ``ProductVersion``
     - ``action.properties.ProductVersion``
   * - ``Service``
     - ``action.properties.Service``
   * - ``WdfVersion``
     - ``action.properties.WdfVersion``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``action.properties.KeyName``
   * - ``parse_timestamp(Date)``
     - ``action.properties.Date``
   * - ``Class``
     - ``action.properties.Class``
   * - ``Directory``
     - ``action.properties.Directory``
   * - ``to_bool(DriverInBox)``
     - ``action.properties.DriverInBox``
   * - ``Hwids``
     - ``action.properties.Hwids``
   * - ``Inf``
     - ``action.properties.Inf``
   * - ``Provider``
     - ``action.properties.Provider``
   * - ``SubmissionId``
     - ``action.properties.SubmissionId``
   * - ``SYSFILE``
     - ``action.properties.SYSFILE``
   * - ``Version``
     - ``action.properties.Version``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``timestamp``
   * - ``parse_timestamp(KeyLastWriteTimestamp)``
     - ``registry.mtime``
   * - ``"Amcache"``
     - ``registry.hive``
   * - ``KeyName``
     - ``action.properties.KeyName``
   * - ``LnkName``
     - ``file.path``
