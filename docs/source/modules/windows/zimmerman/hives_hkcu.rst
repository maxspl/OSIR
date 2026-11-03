hives_hkcu
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:hkcu`` | name_rex: ``r"--hives_*\w*\.csv"``

Description
-----------

Parsing of registry hives artifact.

Timeline
--------

.. _tl-windows-zimmerman-hives-registry-value:
.. _tl-windows-zimmerman-hives-user-account:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `registry-value <rel-windows-zimmerman-hives-registry-value_>`_
     - ``Registry value {registry.value} exists in key {registry.path}``
   * - ``user-account``
     - ``User account {user.name} (RID {user.id}) exists in SAM``

Relationships
-------------

.. _rel-windows-zimmerman-hives-registry-value:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `registry-value <tl-windows-zimmerman-hives-registry-value_>`_
     - ``registry.path``
     - ``registry.value``
     - ``contains``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows Registry"``
     - ``event.provider``
   * - ``KeyPath``
     - ``registry.path``
   * - ``ValueName``
     - ``registry.value``
   * - ``ValueType``
     - ``registry.data.type``
   * - ``HiveType``
     - ``registry.hive``
   * - ``HivePath``
     - ``action.properties.HivePath``
   * - ``Description``
     - ``action.properties.Description``
   * - ``Category``
     - ``action.properties.Category``
   * - ``Comment``
     - ``action.properties.Comment``
   * - ``ValueData``
     - ``action.properties.value_data``
   * - ``ValueData2``
     - ``action.properties.ValueData2``
   * - ``ValueData3``
     - ``action.properties.ValueData3``
   * - ``to_bool(Recursive)``
     - ``action.properties.Recursive``
   * - ``to_bool(Deleted)``
     - ``action.properties.Deleted``
   * - ``PluginDetailFile``
     - ``action.properties.PluginDetailFile``
   * - ``parse_timestamp(LastWriteTimestamp)``
     - ``timestamp``
   * - ``BatchKeyPath``
     - ``registry.path``
   * - ``BatchValueName``
     - ``registry.value``
   * - ``"SAM"``
     - ``registry.hive``
   * - ``UserId``
     - ``user.id``
   * - ``UserName``
     - ``user.name``
   * - ``FullName``
     - ``user.full_name``
   * - ``InternetUserName``
     - ``user.email``
   * - ``PasswordHint``
     - ``action.properties.PasswordHint``
   * - ``Groups``
     - ``action.properties.Groups``
   * - ``Comment``
     - ``action.properties.Comment``
   * - ``UserComment``
     - ``action.properties.UserComment``
   * - ``HomeDirectory``
     - ``action.properties.HomeDirectory``
   * - ``to_bool(ValidUserId)``
     - ``action.properties.ValidUserId``
   * - ``to_int(InvalidLoginCount)``
     - ``action.properties.InvalidLoginCount``
   * - ``to_int(TotalLoginCount)``
     - ``action.properties.TotalLoginCount``
   * - ``to_bool(ResetData)``
     - ``action.properties.ResetData``
   * - ``to_bool(AccountDisabled)``
     - ``action.properties.AccountDisabled``
   * - ``to_bool(HomeDirectoryRequired)``
     - ``action.properties.HomeDirectoryRequired``
   * - ``to_bool(PasswordNotRequired)``
     - ``action.properties.PasswordNotRequired``
   * - ``to_bool(TempDuplicateAccount)``
     - ``action.properties.TempDuplicateAccount``
   * - ``to_bool(NormalUserAccount)``
     - ``action.properties.NormalUserAccount``
   * - ``to_bool(MnsLogonAccount)``
     - ``action.properties.MnsLogonAccount``
   * - ``to_bool(InterdomainTrustAccount)``
     - ``action.properties.InterdomainTrustAccount``
   * - ``to_bool(WorkstationTrustAccount)``
     - ``action.properties.WorkstationTrustAccount``
   * - ``to_bool(ServerTrustAccount)``
     - ``action.properties.ServerTrustAccount``
   * - ``to_bool(PasswordDoesNotExpire)``
     - ``action.properties.PasswordDoesNotExpire``
   * - ``to_bool(AutoLocked)``
     - ``action.properties.AutoLocked``
   * - ``parse_timestamp(CreatedOn)``
     - ``timestamp``
   * - ``parse_timestamp(LastLoginTime)``
     - ``action.properties.LastLoginTime``
   * - ``parse_timestamp(LastPasswordChange)``
     - ``action.properties.LastPasswordChange``
   * - ``parse_timestamp(LastIncorrectPassword)``
     - ``action.properties.LastIncorrectPassword``
   * - ``parse_timestamp(ExpiresOn)``
     - ``action.properties.ExpiresOn``
