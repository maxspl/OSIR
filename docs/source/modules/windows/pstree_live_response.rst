pstree_live_response
====================

.. tip:: Ingestion into Splunk.

   **``windows:live_response:pstree``**

   * name_rex: ``nodes\.jsonl$``
   * path_suffix: ``pstree_live_response``
   * sourcetype: ``windows:live_response:pstree``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``pstree_live_response``
   * normalize: ``ecs_normalize/windows/pstree_nodes.vrl``

Description
-----------

Parse processes1.csv to produce pstree

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
