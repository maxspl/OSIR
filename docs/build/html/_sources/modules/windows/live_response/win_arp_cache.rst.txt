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
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows ARP Cache"``
     - ``event.provider``
   * - ``"arp"``
     - ``network.protocol``
   * - ``"ipv4"``
     - ``network.type``
   * - ``type``
     - ``action.properties.type``
   * - ``interface_ip``
     - ``source.ip``
   * - ``[to_string!(.interface_ip)]``
     - ``host.ip``
   * - ``interface_index``
     - ``action.properties.interface_index``
   * - ``ip_address``
     - ``destination.ip``
   * - ``downcase(replace(to_string!(.mac_address), "-", ":"))``
     - ``destination.mac``
   * - ``"ipv6"``
     - ``network.type``
   * - ``entry_type``
     - ``action.properties.entry_type_raw``
