IIS
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``dissect:windows:iis`` | name_rex: ``r"--IIS\.jsonl$"``

Description
-----------

Parse IIS from DFIR ORC restore\_fs using Dissect plugin

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
   * - ``{}``
     - ``event``
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``del(._recorddescriptor)``
     - ``action.properties.recorddescriptor``
   * - ``del(._classification)``
     - ``action.properties.classification``
   * - ``custom``
     - 
