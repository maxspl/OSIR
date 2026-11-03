pstree_live_response
====================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:pstree`` | name_rex: ``r"nodes\.jsonl$"``

Description
-----------

Parse processes1.csv to produce pstree

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
