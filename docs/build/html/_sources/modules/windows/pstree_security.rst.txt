pstree_security
===============

.. tip:: Ingestion into Splunk.

   **``windows:evtx:pstree``**

   * name_rex: ``nodes\.jsonl$``
   * path_suffix: ``pstree_security``
   * sourcetype: ``windows:evtx:pstree``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``pstree_security``
   * normalize: ``ecs_normalize/windows/pstree_nodes.vrl``

Description
-----------

Parse output of EVTX module to build process tree from security.evtx - event ID 4688

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
