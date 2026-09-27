pstree_security
===============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:evtx:pstree`` | name_rex: ``nodes\.jsonl$``

Description
-----------

Parse output of EVTX module to build process tree from security.evtx - event ID 4688

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
