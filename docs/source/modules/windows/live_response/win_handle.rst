win_handle
==========

.. tip:: Ingestion into Splunk.

   **``windows:live_response:handle``**

   * name_rex: ``--win_handle\.jsonl$``
   * path_suffix: ``win_handle``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``HANDLE``
   * normalize: ``ecs_normalize/windows/live_response/handle.vrl``

Description
-----------

Parse handle from DFIR ORC (handle.exe /a command)

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
