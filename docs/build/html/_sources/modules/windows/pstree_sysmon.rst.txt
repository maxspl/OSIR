pstree_sysmon
=============

.. tip:: Ingestion into Splunk.

   **``windows:sysmon:pstree``**

   * name_rex: ``nodes\.jsonl$``
   * path_suffix: ``pstree_sysmon``
   * sourcetype: ``windows:sysmon:pstree``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``pstree_sysmon``
   * normalize: ``ecs_normalize/windows/pstree_nodes.vrl``

Description
-----------

Parse output of EVTX module to build process tree from the Sysmon operational channel - event ID 1

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
