win_arp_cache
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:arp_cache`` | name_rex: ``r"--win_arp_cache\.jsonl$"``

Description
-----------

Parse arp\_cache.txt from DFIR ORC (arp -a command)

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
   * - ``custom``
     - 
   * - ``"windows.arp_cache"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[network]``
     - ``event.category``
   * - ``[info, arp]``
     - ``event.type``
   * - ``"success"``
     - ``event.outcome``
   * - ``"Windows ARP Cache"``
     - ``event.provider``
   * - ``"arp"``
     - ``network.protocol``
   * - ``"ipv4"``
     - ``network.type``
   * - ``custom``
     - 
   * - ``to_string!(del(.interface_index))``
     - ``network.Ext.arp.interface_index``
   * - ``custom``
     - 
