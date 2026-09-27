hives_hkcu
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:registry:kcu`` | name_rex: ``--hives_*\w*\.csv``

Description
-----------

Parsing of registry hives artifact.

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
   * - ``to_string!(del(.BatchKeyPath))``
     - ``registry.path``
   * - ``to_string!(del(.BatchValueName))``
     - ``registry.value``
   * - ``to_string!(del(.HivePath))``
     - ``registry.hive``
   * - ``to_string!(del(.HiveType))``
     - ``registry.hive_type``
   * - ``to_string!(del(.KeyPath))``
     - ``registry.key_path``
   * - ``to_string!(del(.KeyName))``
     - ``registry.key_name``
   * - ``to_string!(del(.ValueName))``
     - ``registry.value_name``
   * - ``to_string!(del(.ValueType))``
     - ``registry.value_type``
   * - ``del(.ValueData)``
     - ``registry.value_data``
   * - ``del(.ValueData2)``
     - ``registry.value_data2``
   * - ``del(.ValueData3)``
     - ``registry.value_data3``
   * - ``to_string!(del(.ValueDataRaw))``
     - ``registry.value_data_raw``
   * - ``to_string!(del(.Category))``
     - ``registry.category``
   * - ``to_string!(del(.Comment))``
     - ``registry.comment``
   * - ``to_string!(del(.Comments))``
     - ``registry.comments``
   * - ``to_string!(del(.PluginDetailFile))``
     - ``registry.plugin_detail_file``
   * - ``to_string!(del(.Recursive))``
     - ``registry.recursive``
   * - ``to_string!(del(.Deleted))``
     - ``registry.deleted``
   * - ``to_string!(del(.ResetData))``
     - ``registry.reset_data``
   * - ``to_string!(del(.FullPath))``
     - ``file.path``
   * - ``to_string!(del(.AbsolutePath))``
     - ``file.path``
   * - ``to_string!(del(.Path))``
     - ``file.path``
   * - ``to_string!(del(.Path1))``
     - ``file.path``
   * - ``to_string!(del(.Path2))``
     - ``file.directory``
   * - ``to_string!(del(.Filename))``
     - ``file.name``
   * - ``to_string!(del(.FileName))``
     - ``file.name``
   * - ``custom``
     - 
   * - ``to_string!(del(.FolderName))``
     - ``file.directory``
   * - ``to_string!(del(.Extension))``
     - ``file.extension``
   * - ``to_string!(del(.ExtensionLastOpened))``
     - ``file.Ext.extension_last_opened_raw``
   * - ``custom``
     - 
   * - ``to_string!(del(.FileSource))``
     - ``file.source``
   * - ``to_string!(del(.Details))``
     - ``file.details``
   * - ``custom``
     - 
   * - ``to_string!(del(.LnkName))``
     - ``file.lnk_name``
   * - ``to_string!(del(.UninstallString))``
     - ``file.uninstall_command``
   * - ``to_string!(del(.Executable))``
     - ``process.executable``
   * - ``to_string!(del(.ProgramName))``
     - ``process.name``
   * - ``to_string!(del(.Program))``
     - ``process.executable``
   * - ``to_string!(del(.App))``
     - ``process.executable``
   * - ``to_string!(del(.ImagePath))``
     - ``process.executable``
   * - ``to_string!(del(.Service))``
     - ``service.name``
   * - ``to_string!(del(.ServiceType))``
     - ``service.service_type``
   * - ``to_string!(del(.StartMode))``
     - ``service.start_mode``
   * - ``to_string!(del(.ServiceDLL))``
     - ``service.service_dll``
   * - ``to_string!(del(.RequiredPrivileges))``
     - ``service.required_privileges``
   * - ``to_string!(del(.NameKeyLastWrite))``
     - ``service.name_key_last_write_raw``
   * - ``to_string!(del(.ParametersKeyLastWrite))``
     - ``service.parameters_key_last_write_raw``
   * - ``custom``
     - 
   * - ``to_string!(del(.FocusTime))``
     - ``process.focus_time_raw``
   * - ``to_string!(del(.JumpListName))``
     - ``process.jumplist_name``
   * - ``to_string!(del(.Url))``
     - ``url.full``
   * - ``to_string!(del(.SearchTerm))``
     - ``url.query``
   * - ``to_string!(del(.Slack))``
     - ``url.slack_raw``
   * - ``to_string!(del(.HostName))``
     - ``host.name``
   * - ``to_string!(del(.Device))``
     - ``device.name``
   * - ``to_string!(del(.DeviceName))``
     - ``device.name``
   * - ``to_string!(del(.DeviceDesc))``
     - ``device.description``
   * - ``to_string!(del(.Manufacturer))``
     - ``device.manufacturer``
   * - ``to_string!(del(.SerialNumber))``
     - ``device.serial_number``
   * - ``to_string!(del(.DiskId))``
     - ``device.disk_id``
   * - ``to_string!(del(.Title))``
     - ``device.model``
   * - ``to_string!(del(.LocationInformation))``
     - ``device.location_information``
   * - ``to_string!(del(.ParentidPrefix))``
     - ``device.parent_id_prefix``
   * - ``to_string!(del(.DriveName))``
     - ``device.volume_drive_name``
   * - ``to_string!(del(.VolumeLabel))``
     - ``device.volume_label``
   * - ``to_string!(del(.DriveType))``
     - ``device.volume_drive_type``
   * - ``to_string!(del(.GuidFolder))``
     - ``device.guid_folder``
   * - ``to_string!(del(.Guid))``
     - ``device.guid``
   * - ``to_string!(del(.DeviceInstanceid))``
     - ``device.instance_id``
   * - ``to_string!(del(.DriverDesc))``
     - ``driver.name``
   * - ``to_string!(del(.DriverVersion))``
     - ``driver.version``
   * - ``to_string!(del(.DriverDate))``
     - ``driver.date_raw``
   * - ``to_string!(del(.ProviderName))``
     - ``driver.vendor``
   * - ``to_string!(del(.FriendlyName))``
     - ``device.friendly_name``
   * - ``to_string!(del(.GatewayMacAddress))``
     - ``network.gateway_mac``
   * - ``to_string!(del(.NetworkName))``
     - ``network.name``
   * - ``to_string!(del(.DNSSuffix))``
     - ``network.domain``
   * - ``to_string!(del(.Alias))``
     - ``network.interface_alias``
   * - ``to_string!(del(.PermanentAddress))``
     - ``network.permanent_address``
   * - ``to_string!(del(.CurrentAddress))``
     - ``network.current_address``
   * - ``to_string!(del(.Protocol))``
     - ``network.transport``
   * - ``to_string!(del(.ProtocolList))``
     - ``network.protocol_list``
   * - ``to_string!(del(.Address))``
     - ``network.address_raw``
   * - ``custom``
     - 
   * - ``to_string!(del(.Action))``
     - ``rule.action``
   * - ``to_string!(del(.Dir))``
     - ``rule.direction``
   * - ``to_string!(del(.Active))``
     - ``rule.active_raw``
   * - ``to_string!(del(.SecurityDescriptor))``
     - ``rule.security_descriptor``
   * - ``to_string!(del(.Source))``
     - ``rule.source``
   * - ``to_string!(del(.TaskState))``
     - ``rule.task_state``
   * - ``to_string!(del(.LastActionResult))``
     - ``rule.last_action_result``
   * - ``to_string!(del(.Username))``
     - ``user.name``
   * - ``to_string!(del(.UserName))``
     - ``user.name``
   * - ``to_string!(del(.InternetUserName))``
     - ``user.email``
   * - ``to_string!(del(.UserId))``
     - ``user.id``
   * - ``to_string!(del(.FullName))``
     - ``user.full_name``
   * - ``to_string!(del(.ProfileImagePath))``
     - ``user.home``
   * - ``to_string!(del(.HomeDirectory))``
     - ``user.home``
   * - ``to_string!(del(.HomeDirectoryRequired))``
     - ``user.home_directory_required``
   * - ``to_string!(del(.AccountDisabled))``
     - ``user.account_disabled``
   * - ``to_string!(del(.AutoLocked))``
     - ``user.auto_locked``
   * - ``to_string!(del(.NormalUserAccount))``
     - ``user.normal_user_account``
   * - ``to_string!(del(.InterdomainTrustAccount))``
     - ``user.interdomain_trust_account``
   * - ``to_string!(del(.MnsLogonAccount))``
     - ``user.mns_logon_account``
   * - ``to_string!(del(.ServerTrustAccount))``
     - ``user.server_trust_account``
   * - ``to_string!(del(.TempDuplicateAccount))``
     - ``user.temp_duplicate_account``
   * - ``to_string!(del(.ValidUserId))``
     - ``user.valid_user_id``
   * - ``to_string!(del(.PasswordDoesNotExpire))``
     - ``user.password_does_not_expire``
   * - ``to_string!(del(.PasswordNotRequired))``
     - ``user.password_not_required``
   * - ``to_string!(del(.PasswordHint))``
     - ``user.password_hint``
   * - ``to_string!(del(.LastIncorrectPassword))``
     - ``user.last_incorrect_password_raw``
   * - ``to_string!(del(.LastLoginTime))``
     - ``user.last_login_time_raw``
   * - ``to_string!(del(.LastLogoffTime))``
     - ``user.last_logoff_time_raw``
   * - ``to_string!(del(.LastLogonTime))``
     - ``user.last_logon_time_raw``
   * - ``to_string!(del(.LastPasswordChange))``
     - ``user.last_password_change_raw``
   * - ``to_string!(del(.TotalLoginCount))``
     - ``user.total_login_count_raw``
   * - ``to_string!(del(.InvalidLoginCount))``
     - ``user.invalid_login_count_raw``
   * - ``to_string!(del(.UserComment))``
     - ``user.comment``
   * - ``to_string!(del(.GroupName))``
     - ``group.name``
   * - ``to_string!(del(.Groups))``
     - ``group.groups_raw``
   * - ``to_string!(del(.Users))``
     - ``group.users_raw``
   * - ``to_string!(del(.ProfileGUID))``
     - ``user.profile_guid``
   * - ``to_string!(del(.DisplayName))``
     - ``package.name``
   * - ``to_string!(del(.DisplayVersion))``
     - ``package.version``
   * - ``to_string!(del(.Publisher))``
     - ``package.organization``
   * - ``to_string!(del(.InstallLocation))``
     - ``package.path``
   * - ``to_string!(del(.InstallSource))``
     - ``package.install_source``
   * - ``to_string!(del(.PackageName))``
     - ``package.id``
   * - ``to_string!(del(.PackageRootFolder))``
     - ``package.root_folder``
   * - ``to_string!(del(.Version))``
     - ``package.version_raw``
   * - ``custom``
     - 
   * - ``to_string!(del(.CreatedOn))``
     - ``event.created_on_raw``
   * - ``to_string!(del(.ExecutedOn))``
     - ``event.executed_on_raw``
   * - ``to_string!(del(.ExecutionTime))``
     - ``event.execution_time_raw``
   * - ``to_string!(del(.ExpiresOn))``
     - ``event.expires_on_raw``
   * - ``to_string!(del(.InstallDate))``
     - ``event.install_date_raw``
   * - ``to_string!(del(.InstallTime))``
     - ``event.install_time_raw``
   * - ``to_string!(del(.InitialTimestamp))``
     - ``event.initial_timestamp_raw``
   * - ``to_string!(del(.Installed))``
     - ``event.installed_raw``
   * - ``to_string!(del(.FirstInstalled))``
     - ``event.first_installed_raw``
   * - ``to_string!(del(.FirstConnectLOCAL))``
     - ``event.first_connect_local_raw``
   * - ``to_string!(del(.LastConnectedLOCAL))``
     - ``event.last_connected_local_raw``
   * - ``to_string!(del(.LastClosed))``
     - ``event.last_closed_raw``
   * - ``to_string!(del(.LastConnected))``
     - ``event.last_connected_raw``
   * - ``to_string!(del(.LastRemoved))``
     - ``event.last_removed_raw``
   * - ``to_string!(del(.LastSeen))``
     - ``event.last_seen_raw``
   * - ``to_string!(del(.LastStart))``
     - ``event.last_start_raw``
   * - ``to_string!(del(.LastStop))``
     - ``event.last_stop_raw``
   * - ``to_string!(del(.LastWriteTimestamp))``
     - ``event.last_write_timestamp_raw``
   * - ``to_string!(del(.LastModified))``
     - ``event.last_modified_raw``
   * - ``to_string!(del(.LastDetectionTime))``
     - ``event.last_detection_time_raw``
   * - ``to_string!(del(.LastExecuted))``
     - ``event.last_executed_raw``
   * - ``custom``
     - 
   * - ``to_string!(del(.EventType))``
     - ``event.reason``
   * - ``to_string!(del(.Source))``
     - ``event.provider``
   * - ``to_string!(del(.Name))``
     - ``event.name``
   * - ``to_string!(del(.Title))``
     - ``event.title``
   * - ``to_string!(del(.Description))``
     - ``event.description``
   * - ``to_string!(del(.Type))``
     - ``event.type_raw``
   * - ``to_string!(del(.UserChoice))``
     - ``event.user_choice_raw``
   * - ``to_string!(del(.BatchKeyPath))``
     - ``registry.path``
   * - ``to_string!(del(.BatchValueName))``
     - ``registry.value``
   * - ``"windows.registry_artifacts"``
     - ``event.dataset``
   * - ``"Windows Registry (generic)"``
     - ``event.provider``
   * - ``[configuration]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"state"``
     - ``event.kind``
   * - ``"success"``
     - ``event.outcome``
   * - ``"windows"``
     - ``event.module``
