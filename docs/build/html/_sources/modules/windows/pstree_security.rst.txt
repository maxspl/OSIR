pstree_security
===============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:evtx:pstree`` | name_rex: ``r"nodes\.jsonl$"``

Description
-----------

Parse output of EVTX module to build process tree from security.evtx - event ID 4688

Timeline
--------

No timeline messages.

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"process_tree_node"``
     - ``event.action``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
