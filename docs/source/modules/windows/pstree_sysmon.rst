pstree_sysmon
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:sysmon:pstree`` | name_rex: ``nodes\.jsonl$``

Description
-----------

Parse output of EVTX module to build process tree from the Sysmon operational channel - event ID 1

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"windows.pstree_nodes"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"process_tree_node"``
     - ``event.action``
   * - ``"success"``
     - ``event.outcome``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
