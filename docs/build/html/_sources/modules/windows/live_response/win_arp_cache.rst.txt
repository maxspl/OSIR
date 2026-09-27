win_arp_cache
=============

.. tip:: Ingestion into Splunk.

   **``windows:live_response:arp_cache``**

   * name_rex: ``--win_arp_cache\.jsonl$``
   * path_suffix: ``win_arp_cache``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``ARP``
   * normalize: ``ecs_normalize/windows/live_response/arp_cache.vrl``

Description
-----------

Parse arp\_cache.txt from DFIR ORC (arp -a command)

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
