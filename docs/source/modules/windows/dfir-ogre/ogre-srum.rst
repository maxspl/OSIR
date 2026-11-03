ogre-srum
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:srum`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of srum - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-srum-app-usage:

.. list-table::
   :header-rows: 1

   * - action.properties.app_id
     - Relation
     - Message
   * - 
     - `app-usage <rel-windows-dfir-ogre-srum-app-usage_>`_
     - ``Application {action.properties.app_id} was used by user {user.id}``

Relationships
-------------

.. _rel-windows-dfir-ogre-srum-app-usage:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `app-usage <tl-windows-dfir-ogre-srum-app-usage_>`_
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
   * - ``parse_timestamp(timestamp)``
     - ``timestamp``
   * - ``to_int(incremental_id)``
     - ``action.properties.auto_inc_id``
   * - ``app_id``
     - ``action.properties.app_id``
   * - ``user_id``
     - ``user.id``
   * - ``to_int(face_time)``
     - ``action.properties.facetime``
   * - ``to_int(foreground_cycle_time)``
     - ``action.properties.foreground_cycle_time``
   * - ``to_int(background_cycle_time)``
     - ``action.properties.background_cycle_time``
   * - ``to_int(foreground_context_switches)``
     - ``action.properties.foreground_context_switches``
   * - ``to_int(background_context_switches)``
     - ``action.properties.background_context_switches``
   * - ``to_int(foreground_bytes_read)``
     - ``action.properties.foreground_bytes_read``
   * - ``to_int(foreground_bytes_written)``
     - ``action.properties.foreground_bytes_written``
   * - ``to_int(background_bytes_read)``
     - ``action.properties.background_bytes_read``
   * - ``to_int(background_bytes_written)``
     - ``action.properties.background_bytes_written``
   * - ``to_int(foreground_num_read_operations)``
     - ``action.properties.foreground_num_read_operations``
   * - ``to_int(foreground_num_write_operations)``
     - ``action.properties.foreground_num_write_options``
   * - ``to_int(background_num_read_operations)``
     - ``action.properties.background_num_read_operations``
   * - ``to_int(background_num_write_operations)``
     - ``action.properties.background_num_write_operations``
   * - ``to_int(foreground_number_of_flushes)``
     - ``action.properties.foreground_number_of_flushes``
   * - ``to_int(background_number_of_flushes)``
     - ``action.properties.background_number_of_flushes``
   * - ``custom``
     - 
