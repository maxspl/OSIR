win_listdlls
============

.. tip:: Ingestion into Splunk.

   **``windows:live_response:dll``**

   * name_rex: ``--win_listdlls\.jsonl$``
   * path_suffix: ``win_listdlls``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``DLL``
   * normalize: ``ecs_normalize/windows/live_response/listdlls.vrl``

Description
-----------

Parse Listdlls.txt from DFIR ORC (Listdlls.exe command)

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
