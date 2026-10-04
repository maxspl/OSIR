ogre-srum
=========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:srum`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of srum - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-srum-app-usage:

.. list-table::
   :header-rows: 1

   * - labels.app_id
     - Relation
     - Message
   * - 
     - `app-usage <rel-windows-srum-app-usage_>`_
     - ``Application {labels.app_id} was used by user {user.id}``

Relationships
-------------

.. _rel-windows-srum-app-usage:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `app-usage <tl-windows-srum-app-usage_>`_
     - ``user.id``
     - ``labels.app_id``
     - ``used``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.srum"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows System Resource Usage Monitor (SRUM)"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``parse_timestamp(timestamp)``
     - ``timestamp``
   * - ``to_int(auto_inc_id)``
     - ``labels.incremental_id``
   * - ``app_id``
     - ``labels.app_id``
   * - ``user_id``
     - ``user.id``
   * - ``to_int(facetime)``
     - ``labels.face_time``
   * - ``to_int(foreground_cycle_time)``
     - ``labels.foreground_cycle_time``
   * - ``to_int(background_cycle_time)``
     - ``labels.background_cycle_time``
   * - ``to_int(foreground_context_switches)``
     - ``labels.foreground_context_switches``
   * - ``to_int(background_context_switches)``
     - ``labels.background_context_switches``
   * - ``to_int(foreground_bytes_read)``
     - ``labels.foreground_bytes_read``
   * - ``to_int(foreground_bytes_written)``
     - ``labels.foreground_bytes_written``
   * - ``to_int(background_bytes_read)``
     - ``labels.background_bytes_read``
   * - ``to_int(background_bytes_written)``
     - ``labels.background_bytes_written``
   * - ``to_int(foreground_num_read_operations)``
     - ``labels.foreground_num_read_operations``
   * - ``to_int(foreground_num_write_options)``
     - ``labels.foreground_num_write_operations``
   * - ``to_int(background_num_read_operations)``
     - ``labels.background_num_read_operations``
   * - ``to_int(background_num_write_operations)``
     - ``labels.background_num_write_operations``
   * - ``to_int(foreground_number_of_flushes)``
     - ``labels.foreground_number_of_flushes``
   * - ``to_int(background_number_of_flushes)``
     - ``labels.background_number_of_flushes``
   * - ``collection_metadata``
     - ``labels.collection_metadata``
   * - ``parse_timestamp(timestamp)``
     - ``timestamp``
   * - ``to_int(incremental_id)``
     - ``labels.incremental_id``
   * - ``app_id``
     - ``labels.app_id``
   * - ``user_id``
     - ``user.id``
   * - ``to_int(face_time)``
     - ``labels.face_time``
   * - ``to_int(foreground_cycle_time)``
     - ``labels.foreground_cycle_time``
   * - ``to_int(background_cycle_time)``
     - ``labels.background_cycle_time``
   * - ``to_int(foreground_context_switches)``
     - ``labels.foreground_context_switches``
   * - ``to_int(background_context_switches)``
     - ``labels.background_context_switches``
   * - ``to_int(foreground_bytes_read)``
     - ``labels.foreground_bytes_read``
   * - ``to_int(foreground_bytes_written)``
     - ``labels.foreground_bytes_written``
   * - ``to_int(background_bytes_read)``
     - ``labels.background_bytes_read``
   * - ``to_int(background_bytes_written)``
     - ``labels.background_bytes_written``
   * - ``to_int(foreground_num_read_operations)``
     - ``labels.foreground_num_read_operations``
   * - ``to_int(foreground_num_write_operations)``
     - ``labels.foreground_num_write_operations``
   * - ``to_int(background_num_read_operations)``
     - ``labels.background_num_read_operations``
   * - ``to_int(background_num_write_operations)``
     - ``labels.background_num_write_operations``
   * - ``to_int(foreground_number_of_flushes)``
     - ``labels.foreground_number_of_flushes``
   * - ``to_int(background_number_of_flushes)``
     - ``labels.background_number_of_flushes``
   * - ``ogre_md``
     - ``labels.ogre_md``
