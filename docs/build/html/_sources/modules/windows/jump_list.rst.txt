jump_list
=========

.. tip:: Ingestion into Splunk.

   **``windows:jumplist``**

   * name_rex: ``\.csv$``
   * path_suffix: ``jump_list``
   * sourcetype: ``windows:files:jumplist``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``JumpList``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/windows/jump_list.vrl``

Description
-----------

Parsing of jump list artifact.

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
