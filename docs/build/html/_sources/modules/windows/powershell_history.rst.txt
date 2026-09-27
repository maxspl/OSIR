powershell_history
==================

.. tip:: Ingestion into Splunk.

   **``windows:powershell_history``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``powershell_history``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``POWERSHELL``
   * normalize: ``ecs_normalize/windows/powershell_history.vrl``

Description
-----------

Parse ConsoleHost\_history.txt

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
