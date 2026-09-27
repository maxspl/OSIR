win_routes
==========

.. tip:: Ingestion into Splunk.

   **``windows:live_response:routes``**

   * name_rex: ``--win_routes\.jsonl$``
   * path_suffix: ``win_routes``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``ROUTES``
   * normalize: ``ecs_normalize/windows/live_response/routes.vrl``

Description
-----------

Parse routes.txt from DFIR ORC (route.exe PRINT command)

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
