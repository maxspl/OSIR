IIS
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:iis`` | name_rex: ``r"--IIS\.jsonl$"``

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
   * - ``"event"``
     - ``event.kind``
   * - ``[web]``
     - ``event.category``
   * - ``[access]``
     - ``event.type``
   * - ``"iis.access"``
     - ``event.dataset``
   * - ``"iis"``
     - ``event.module``
   * - ``"unknown"``
     - ``event.outcome``
   * - ``custom``
     - 
   * - ``del(._recorddescriptor)``
     - ``event.Ext.iis.recorddescriptor``
   * - ``del(._classification)``
     - ``event.Ext.iis.classification``
   * - ``custom``
     - 
