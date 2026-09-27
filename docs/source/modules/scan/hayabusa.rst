hayabusa
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``hayabusa`` | name_rex: ``\.jsonl$``

Description
-----------

Hayabusa scan of evtx files

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
   * - ``"event"``
     - ``event.kind``
   * - ``"hayabusa"``
     - ``event.module``
   * - ``"hayabusa"``
     - ``agent.type``
   * - ``custom``
     - 
   * - ``del(.Computer)``
     - ``host.name``
   * - ``custom``
     - 
   * - ``to_string!(del(.RecordID))``
     - ``winlog.record_id``
   * - ``del(.Details)``
     - ``hayabusa.details``
   * - ``del(.ExtraFieldInfo)``
     - ``hayabusa.extra``
   * - ``custom``
     - 
