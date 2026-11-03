srum_ecmd
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:srum`` | name_rex: ``r"\.csv$"``

Description
-----------

Parsing of SRUDB.dat (SRUM) with SrumECmd

Timeline
--------

.. _tl-windows-zimmerman-srum_ecmd-app-usage:

.. list-table::
   :header-rows: 1

   * - action.properties.app_id
     - Relation
     - Message
   * - 
     - `app-usage <rel-windows-zimmerman-srum_ecmd-app-usage_>`_
     - ``Application {action.properties.app_id} was used by user {user.id}``

Relationships
-------------

.. _rel-windows-zimmerman-srum_ecmd-app-usage:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `app-usage <tl-windows-zimmerman-srum_ecmd-app-usage_>`_
     - ``user.id``
     - ``action.properties.app_id``
     - ``used``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows System Resource Usage Monitor (SRUM)"``
     - ``event.provider``
   * - ``parse_timestamp(Timestamp)``
     - ``timestamp``
   * - ``to_int(Id)``
     - ``action.properties.auto_inc_id``
   * - ``AppId``
     - ``action.properties.app_id``
   * - ``ExeInfo``
     - ``action.properties.exe_info``
   * - ``ExeInfoDescription``
     - ``action.properties.exe_info_description``
   * - ``ExeTimestamp``
     - ``action.properties.exe_timestamp``
   * - ``Sid``
     - ``user.id``
   * - ``UserName``
     - ``user.name``
   * - ``to_int(UserId)``
     - ``action.properties.user_id``
   * - ``to_int(FaceTime)``
     - ``action.properties.facetime``
   * - ``to_int(ForegroundCycleTime)``
     - ``action.properties.foreground_cycle_time``
   * - ``to_int(BackgroundCycleTime)``
     - ``action.properties.background_cycle_time``
   * - ``to_int(ForegroundContextSwitches)``
     - ``action.properties.foreground_context_switches``
   * - ``to_int(BackgroundContextSwitches)``
     - ``action.properties.background_context_switches``
   * - ``to_int(ForegroundBytesRead)``
     - ``action.properties.foreground_bytes_read``
   * - ``to_int(ForegroundBytesWritten)``
     - ``action.properties.foreground_bytes_written``
   * - ``to_int(BackgroundBytesRead)``
     - ``action.properties.background_bytes_read``
   * - ``to_int(BackgroundBytesWritten)``
     - ``action.properties.background_bytes_written``
   * - ``to_int(ForegroundNumReadOperations)``
     - ``action.properties.foreground_num_read_operations``
   * - ``to_int(ForegroundNumWriteOperations)``
     - ``action.properties.foreground_num_write_options``
   * - ``to_int(BackgroundNumReadOperations)``
     - ``action.properties.background_num_read_operations``
   * - ``to_int(BackgroundNumWriteOperations)``
     - ``action.properties.background_num_write_operations``
   * - ``to_int(ForegroundNumberOfFlushes)``
     - ``action.properties.foreground_number_of_flushes``
   * - ``to_int(BackgroundNumberOfFlushes)``
     - ``action.properties.background_number_of_flushes``
   * - ``custom``
     - 
