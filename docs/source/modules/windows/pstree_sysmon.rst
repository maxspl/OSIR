pstree_sysmon
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:sysmon:pstree`` | name_rex: ``r"nodes\.jsonl$"``

Description
-----------

Parse output of EVTX module to build process tree from the Sysmon operational channel - event ID 1

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
