win_enumlocs
============

.. tip:: Ingestion into Splunk.

   **``windows:live_response:enumlocs``**

   * name_rex: ``--win_enumlocs\.jsonl$``
   * path_suffix: ``win_enumlocs``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``event.start``, ``host.Ext.enumlocs.start_time``, ``host.Ext.enumlocs.start_time_raw``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%fZ``
   * artifact: ``ENUMLOCS``
   * normalize: ``ecs_normalize/windows/live_response/enumlocs.vrl``

Description
-----------

Parse Enumlocs.txt from DFIR ORC

Timeline
--------

Placeholder table for the messages created for the timeline.

.. list-table::
   :header-rows: 1

   * - Timeline
     - ECS field
     - Message
   * -
     -
     -

Fields
------

Placeholder table for the output fields.

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * -
     -
